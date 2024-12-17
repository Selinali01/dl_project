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
        # Changed lang parameter to "zh" for Chinese
        q, img_path, choices_str = sivqa_utils.format_question(
            question, 
            lang="zh",  # Changed to Chinese
            show_food_name=show_food_name
        )
        
        # Use Chinese template formatting
        prompt = sivqa_utils.format_text_prompt(q, choices_str, template=template, lang="zh")
        
        # If prompt is a list (for templates 2-4), join with appropriate formatting
        if isinstance(prompt, list):
            system_prompt = prompt[0]
            user_expectation = prompt[1]
        else:
            system_prompt = prompt
            user_expectation = "请只提供字母选项作为答案。"  # Chinese instruction

        # Construct messages for API call
        messages = [
            {
                "role": "system",
                "content": "你是一个帮助回答食物图片相关问题的智能助手。"  # Chinese system message
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
            print(f"处理问题时出错：{e}")  # Chinese error message
            answer_idx = int(question['answer'])
            return {
                "question_id": question["question_id"],
                "response": "错误",  # Chinese error message
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
                       help="包含数据集的目录")  # Chinese help text
    parser.add_argument("--output_dir", 
                       default="/Users/selinali/dl_project/FoodieQA/output",
                       help="结果输出目录")  # Chinese help text
    parser.add_argument("--eval_file", 
                       default="sivqa_tidy.json",
                       help="评估文件名称")  # Chinese help text
    parser.add_argument("--template", 
                       type=int, 
                       default=0,
                       help="提示模板编号 (0-4)")  # Chinese help text
    parser.add_argument("--show_food_name", 
                       action="store_true", 
                       default=False,
                       help="是否在提示中显示食物名称")  # Chinese help text
    parser.add_argument("--api_key", 
                       type=str, 
                       default="",
                       help="OpenAI API密钥 (如果使用环境变量则可选)")  # Chinese help text
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
        output_file = os.path.join(args.output_dir, f'resultszh_template{args.template}.jsonl')
        with open(output_file, 'w') as f:
            for r in results:
                f.write(json.dumps(r) + '\n')

    # Calculate and save final accuracy
    accuracy = evaluator.total_correct / evaluator.total_questions
    print(f"最终准确率：{accuracy:.2%}")  # Chinese output

    # Save summary
    summary = {
        "template": args.template,
        "total_questions": evaluator.total_questions,
        "total_correct": evaluator.total_correct,
        "accuracy": accuracy,
        "show_food_name": args.show_food_name
    }
    
    with open(os.path.join(args.output_dir, f'summaryzh_template{args.template}.json'), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()