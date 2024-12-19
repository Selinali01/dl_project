import openai
import os
import json
from tqdm import tqdm
import sivqa_utils
from dotenv import load_dotenv
import argparse

load_dotenv()

class GPT4oEvaluator:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.total_correct = 0
        self.total_questions = 0

    def evaluate_question(self, question, data_dir, template=0, show_food_name=False):
        # Get formatted question, image path, and choices using sivqa_utils
        q, img_path, choices_str = sivqa_utils.format_question(
            question, 
            lang="en",
            show_food_name=show_food_name
        )
        
        # Use their template formatting
        prompt = sivqa_utils.format_text_prompt(q, choices_str, template=template, lang="en")
        
        # If prompt is a list (for templates 2-4), join with appropriate formatting
        if isinstance(prompt, list):
            system_prompt = prompt[0]
            user_expectation = prompt[1]
        else:
            system_prompt = prompt
            user_expectation = "Please provide only the letter choice as your answer."

        # Construct messages for API call
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions about food images."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{self._encode_image(os.path.join(data_dir, img_path))}"}
                    },
                    {
                        "type": "text",
                        "text": system_prompt + "\n" + user_expectation
                    }
                ]
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300
            )
            answer = response.choices[0].message.content.strip()
            
            # Extract just the letter from response
            answer = self._extract_letter(answer)
            
            # Convert answer string to int before using it
            answer_idx = int(question['answer'])
            ground_truth = chr(ord('A') + answer_idx)
            is_correct = int(answer == ground_truth)
            self.total_correct += is_correct
            self.total_questions += 1

            return {
                "question_id": question["question_id"],
                "response": answer,
                "ground_truth": ground_truth,
                "correct": is_correct
            }

        except Exception as e:
            print(f"Error processing question: {e}")
            # Also fix the ground truth calculation in the error case
            answer_idx = int(question['answer'])
            return {
                "question_id": question["question_id"],
                "response": "ERROR",
                "ground_truth": chr(ord('A') + answer_idx),
                "correct": 0
            }

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            import base64
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _extract_letter(self, response):
        """Extract the first A, B, C, or D from the response"""
        for char in response:
            if char in 'ABCD':
                return char
        return 'X'  # Return X if no valid letter found

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", 
                       default="/Users/selinali/dl_project/FoodieQA/data_folder",
                       help="Directory containing the dataset")
    parser.add_argument("--output_dir", 
                       default="/Users/selinali/dl_project/FoodieQA/output",
                       help="Output directory for results")
    parser.add_argument("--eval_file", 
                       default="sivqa_test.json",
                       help="Evaluation file name")
    parser.add_argument("--template", 
                       type=int, 
                       default=0,
                       help="Prompt template number (0-4)")
    parser.add_argument("--show_food_name", 
                       action="store_true", 
                       default=False,
                       help="Whether to show food name in prompt")
    parser.add_argument("--api_key", 
                       type=str, 
                       default="",
                       help="OpenAI API key (optional if using env var)")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize evaluator
    evaluator = GPT4oEvaluator(api_key=args.api_key if args.api_key else None)

    # Load questions using the specified eval file
    questions = sivqa_utils.read_sivqa(args.data_dir, args.eval_file)


    # Evaluate all questions
    results = []
    for question in tqdm(questions):
        result = evaluator.evaluate_question(
            question,
            args.data_dir,
            template=args.template,
            show_food_name=args.show_food_name
        )
        results.append(result)

        # Save results after each question (in case of interruption)
        output_file = os.path.join(args.output_dir, f'results_template{args.template}.jsonl')
        with open(output_file, 'w') as f:
            for r in results:
                f.write(json.dumps(r) + '\n')

    # Calculate and save final accuracy
    accuracy = evaluator.total_correct / evaluator.total_questions
    print(f"Final accuracy: {accuracy:.2%}")

    # Save summary
    summary = {
        "template": args.template,
        "total_questions": evaluator.total_questions,
        "total_correct": evaluator.total_correct,
        "accuracy": accuracy,
        "show_food_name": args.show_food_name
    }
    
    with open(os.path.join(args.output_dir, f'summary_template{args.template}.json'), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()