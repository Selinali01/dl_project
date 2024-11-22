import openai
import os
import json
from PIL import Image
import base64
from io import BytesIO
from tqdm import tqdm
import sivqa_utils
import textqa_utils
import argparse
class Evaluator(object):
    def __init__(self, args):
        self.client = openai.OpenAI(api_key=args.api_key)
        self.args = args
    def encode_image(self, image_path):
        """Encode an image file to base64 for API usage."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    def eval_question(self, sivqa, idx, data_dir):
        """Send a question and image to GPT-4 Vision API for evaluation."""
        question = sivqa[idx]
        # Build the text prompt
        prompt = f"""Question: {question['question']}\nOptions: A, B, C, D.\nPlease choose the most appropriate answer. IMPORTANT FORMATTING INSTRUCTIONS:
                    Make sure that your final output is ONLY a single letter, indicating your multiple answer choice. Do not provide any reasoning, explanation, extra character(s) in your final response, and ONLY output either A, B, C or D. For example, if the question is: The food in the picture belongs to which cuisine?
                    A. Sichuan cuisine [Correct]
                    B. Xinjiang cuisine
                    C. Cantonese cuisine
                    D. Northern Chinese cuisine
                    Then your output should be: A"""
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that answers questions based on images and text."
            }
        ]
        # Process image if not hidden
        if not self.args.hide_img:
            img_file = (
                question["food_meta"]["web_file"]
                if self.args.use_web_img and "web_file" in question["food_meta"]
                else question["food_meta"]["food_file"]
            )
            image_path = os.path.join(data_dir, img_file)
            # Handle image content
            base64_image = self.encode_image(image_path)
            # Add image and prompt in the correct format
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300
            )
            generated_response = response.choices[0].message.content
        except Exception as e:
            print(f"Error during API call for question {idx}: {str(e)}")
            generated_response = "N/A"
        return {
            "response": generated_response,
            "qid": question["question_id"]
        }
def main(args):
    evaluator = Evaluator(args)
    # Read data
    data_dir = args.data_dir
    eval_file = args.eval_file
    sivqa = sivqa_utils.read_sivqa(data_dir, eval_file)
    # Prepare output file
    out_file_name = f"sivqa_{args.model_name}_prompt{args.template}_{args.lang}.jsonl"
    os.makedirs(args.out_dir, exist_ok=True)
    # Evaluate
    print(f"Evaluating model on {len(sivqa)} questions...")
    with open(os.path.join(args.out_dir, out_file_name), "w", encoding="utf-8") as f:
        for idx in tqdm(range(len(sivqa))):
            result = evaluator.eval_question(sivqa, idx, data_dir)
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(f"Results saved to {os.path.join(args.out_dir, out_file_name)}")
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    # argparser.add_argument("--api_key", type=str, default="", help="OpenAI API key")
    argparser.add_argument("--data_dir", default="FoodieQA\\data_folder",
                          help="Directory containing the dataset")
    argparser.add_argument("--eval_file", type=str, default="test.json",
                          help="Evaluation file name")
    argparser.add_argument("--out_dir", default="FoodieQA\\output",
                          help="Output directory for results")
    argparser.add_argument("--model_name", default="gpt-4o-mini",
                          help="Model name (currently only supports gpt-4-vision)")
    argparser.add_argument("--show_food_name", action="store_true", default=False,
                          help="Whether to show food name in prompt")
    argparser.add_argument("--hide_img", action="store_true", default=False,
                          help="Whether to hide images from the model")
    argparser.add_argument("--template", type=int, default=0,
                          help="Prompt template number")
    argparser.add_argument("--lang", type=str, default="zh",
                          help="Language for the evaluation")
    argparser.add_argument("--use_web_img", action="store_true", default=False,
                          help="Whether to use web images instead of local images")
    args = argparser.parse_args()
    main(args)