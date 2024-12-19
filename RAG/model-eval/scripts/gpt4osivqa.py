import openai
import os
import json
from tqdm import tqdm
import sivqa_utils
from dotenv import load_dotenv
import argparse
import re

load_dotenv()

class GPT4oEvaluator:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.total_correct = 0
        self.total_questions = 0

    def _extract_letter(self, response):
        """Extract any A, B, C, or D that appears after 'Final Answer:', ignoring other formatting"""
        
        # Look for "Final Answer:" followed by any characters until we find A, B, C, or D
        match = re.search(r"Final Answer:.*?([ABCD])", response, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        return 'X'  # Return X if no valid letter found

    def evaluate_question(self, question, data_dir, template=0, show_food_name=False):
        # Get formatted question, image path, and choices using sivqa_utils
        q, img_path, choices_str, food_name = sivqa_utils.format_question(
            question, 
            lang="zh",
            show_food_name=show_food_name
        )
        
        # Use their template formatting
        prompt = sivqa_utils.format_text_prompt(q, choices_str, template=template, lang="zh", food_name = food_name)        
        # If prompt is a list (for templates 2-4), join with appropriate formatting
        if isinstance(prompt, list):
            system_prompt = prompt[0]
            user_expectation = prompt[1]
        else:
            system_prompt = prompt
            user_expectation = "After your analysis, please end your response with 'Final Answer: [X]' where X is your chosen option (A, B, C, or D)."

        # Construct messages for API call
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions about food images.
                When answering, please:
                1. Describe what you see in the image
                2. Analyze the possible options
                3. Explain your reasoning
                4. End your response with 'Final Answer: [X]' where X is your chosen option (A, B, C, or D)"""
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
                max_tokens=500,
                temperature=0.7
            )
            full_response = response.choices[0].message.content.strip()
            
            # Print the full response for debugging
            print("\n=== Question and Response ===")
            print(f"Question ID: {question['question_id']}")
            print(f"Question: {q}")
            print(f"Choices:\n{choices_str}")
            print(f"Model's Response:\n{full_response}")
            
            # Extract just the letter from response
            answer = self._extract_letter(full_response)
            print(f"Extracted Answer: {answer}")
            
            # Convert answer string to int before using it
            answer_idx = int(question['answer'])
            ground_truth = chr(ord('A') + answer_idx)
            is_correct = int(answer == ground_truth)
            self.total_correct += is_correct
            self.total_questions += 1
            
            print(f"Ground Truth: {ground_truth}")
            print(f"Correct: {is_correct}")
            print("=====================\n")

            return {
                "question_id": question["question_id"],
                "question": q,
                "choices": choices_str,
                "response": answer,
                "full_response": full_response,
                "ground_truth": ground_truth,
                "correct": is_correct
            }

        except Exception as e:
            print(f"Error processing question: {e}")
            answer_idx = int(question['answer'])
            return {
                "question_id": question["question_id"],
                "question": q,
                "choices": choices_str,
                "response": "ERROR",
                "full_response": str(e),
                "ground_truth": chr(ord('A') + answer_idx),
                "correct": 0
            }

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            import base64
            return base64.b64encode(image_file.read()).decode('utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", 
                       default="C:\\Users\\choyd\cs5787\\final\\dl_project\\FoodieQA\\data_folder",
                       help="Directory containing the dataset")
    parser.add_argument("--output_dir", 
                       default="C:\\Users\\choyd\cs5787\\final\\dl_project\\FoodieQA\\output",
                       help="Output directory for results")
    parser.add_argument("--eval_file", 
                       default="sivqa_test.json",
                       help="Evaluation file name")
    parser.add_argument("--template", 
                       type=int, 
                       default=6,
                       help="Prompt template number")
    parser.add_argument("--show_food_name", 
                       action="store_true", 
                       default=True,
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
<<<<<<< HEAD
        output_file = os.path.join(args.output_dir, f'baidu_results_template{args.template}_zh.jsonl')
=======
        output_file = os.path.join(args.output_dir, f'results_template{args.template}_verbose.jsonl')
>>>>>>> CoT
        with open(output_file, 'w') as f:
            for r in results:
                f.write(json.dumps(r) + '\n')

    # Calculate and save final accuracy
    accuracy = evaluator.total_correct / evaluator.total_questions
    print(f"\nFinal accuracy: {accuracy:.2%}")

    # Save summary
    summary = {
        "template": args.template,
        "total_questions": evaluator.total_questions,
        "total_correct": evaluator.total_correct,
        "accuracy": accuracy,
        "show_food_name": args.show_food_name
    }
    
<<<<<<< HEAD
    with open(os.path.join(args.output_dir, f'baidu_summary_template{args.template}_zh.json'), 'w') as f:
=======
    with open(os.path.join(args.output_dir, f'summary_template{args.template}_verbose.json'), 'w') as f:
>>>>>>> CoT
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()