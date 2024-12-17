import openai
import os
import json
from tqdm import tqdm
import sivqa_utils
from dotenv import load_dotenv
import argparse
import re
import base64
import datetime

load_dotenv()

class DishIdentifier:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.processed_questions = 0

    def _extract_dishes(self, response):
        """Extract the three most likely dishes from the response"""
        # Try different potential formats
        patterns = [
            r"most likely dishes are:\s*\[(.*?)\]",  # [dish1, dish2, dish3]
            r"most likely dishes are:\s*(.*?)(?:\n|$)",  # dish1, dish2, dish3
            r"Selected dishes:\s*(.*?)(?:\n|$)",  # Selected dishes: dish1, dish2, dish3
            r"Top 3 dishes:\s*(.*?)(?:\n|$)",  # Top 3 dishes: dish1, dish2, dish3
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                # Split on comma or 、, remove brackets, quotes, and whitespace
                dishes = [dish.strip('[] "\',\'') for dish in re.split(r'[,、]', match.group(1))]
                # Remove empty strings and take only first 3
                dishes = [d for d in dishes if d.strip()][:3]
                if len(dishes) == 3:
                    return dishes
                
        return ["无法识别", "无法识别", "无法识别"]  # "Unable to identify" in Chinese

    def _format_dishes_prompt(self, all_dishes):
        """Format the available dishes into a clear prompt"""
        prompt = "Available dishes by cuisine type:\n\n"
        for cuisine, dishes in all_dishes['dishes_by_cuisine'].items():
            if dishes:  # Only include cuisines with dishes
                prompt += f"{cuisine}:\n"
                for dish in dishes:
                    prompt += f"- {dish}\n"
                prompt += "\n"
        return prompt

    def identify_dishes(self, question, data_dir, all_dishes):
        # Get formatted question and image path
        _, img_path, _ = sivqa_utils.format_question(
            question, 
            lang="en",
            show_food_name=False
        )

        # Format available dishes
        dishes_prompt = self._format_dishes_prompt(all_dishes)

        # Construct the prompt
        system_prompt = f"""You are a helpful chef AI assistant analyzing Chinese dishes.
        
        IMPORTANT: You must ONLY select dishes from the following list. Do not suggest any dishes not in this list:

        {dishes_prompt}

        Please examine this food image carefully and:
        1. List visible ingredients and components
        2. Note cooking methods and techniques visible
        3. Observe presentation style and regional characteristics
        4. Based on these observations, select exactly three dishes from the provided list above
        
        Your response MUST end with exactly this format:
        Selected dishes: [dish1, dish2, dish3]
        
        Where dish1, dish2, and dish3 are chosen from the provided list."""

        messages = [
            {
                "role": "system",
                "content": system_prompt
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
                        "text": "Please analyze this food image and identify exactly three dishes from the provided list that this image most likely represents, in order of probability."
                    }
                ]
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            full_response = response.choices[0].message.content.strip()
            
            # Print the full response for debugging
            print("\n=== Question and Response ===")
            print(f"Question ID: {question['question_id']}")
            print(f"Actual Dish: {question['food_name']}")
            print(f"Model's Response:\n{full_response}")
            
            # Extract the predicted dishes
            predicted_dishes = self._extract_dishes(full_response)
            print(f"Extracted Dishes: {predicted_dishes}")
            print("=====================\n")

            self.processed_questions += 1

            return {
                "question_id": question["question_id"],
                "actual_dish": question["food_name"],
                "predicted_dishes": predicted_dishes,
                "full_response": full_response
            }

        except Exception as e:
            print(f"Error processing question: {e}")
            return {
                "question_id": question["question_id"],
                "actual_dish": question["food_name"],
                "predicted_dishes": ["错误", "错误", "错误"],  # "Error" in Chinese
                "full_response": str(e)
            }

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

def load_dishes_data(data_dir):
    dishes_file = os.path.join(data_dir, "dishes_data.json")
    with open(dishes_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", 
                       default="/Users/selinali/dl_project/FoodieQA/data_folder",
                       help="Directory containing the dataset")
    parser.add_argument("--output_dir", 
                       default="/Users/selinali/dl_project/FoodieQA/output",
                       help="Output directory for results")
    parser.add_argument("--eval_file", 
                       default="sivqa_tidy.json",
                       help="Evaluation file name")
    parser.add_argument("--api_key", 
                       type=str, 
                       default="",
                       help="OpenAI API key (optional if using env var)")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize identifier
    identifier = DishIdentifier(api_key=args.api_key if args.api_key else None)

    # Load questions and dishes data
    questions = sivqa_utils.read_sivqa(args.data_dir, args.eval_file)
    all_dishes = load_dishes_data(args.data_dir)

    # Process all questions
    results = []
    for question in tqdm(questions):
        result = identifier.identify_dishes(
            question,
            args.data_dir,
            all_dishes
        )
        results.append(result)

        # Save results after each question (in case of interruption)
        output_file = os.path.join(args.output_dir, 'dish_identification_results.jsonl')
        with open(output_file, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # Save summary
    summary = {
        "total_questions": identifier.processed_questions,
        "timestamp": str(datetime.datetime.now())
    }
    
    with open(os.path.join(args.output_dir, 'dish_identification_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()