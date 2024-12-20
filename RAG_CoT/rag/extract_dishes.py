import json
import os
from collections import defaultdict
from typing import Dict, List, Set

def extract_unique_dishes(file_path: str) -> Dict:
    """
    Extract unique dishes and their metadata from the FoodieQA dataset.
    
    Args:
        file_path: Path to the sivqa_tidy.json file
    
    Returns:
        Dict containing unique dishes and their metadata
    """
    dishes = {}
    question_types_per_dish = defaultdict(set)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # First pass: Collect all questions for each dish
        for entry in data:
            food_name = entry['food_meta']['food_name']
            question_types_per_dish[food_name].add(entry['question_type'])
            
            # Only add dish once to our dishes dictionary
            if food_name not in dishes:
                meta = entry['food_meta']
                dishes[food_name] = {
                    'name': {
                        'chinese': food_name,
                        'english': None  # Could be added later
                    },
                    'metadata': {
                        'cuisine_type': meta.get('food_type', ''),
                        'main_ingredients': meta.get('main_ingredient', []),
                        'id': meta.get('id', ''),
                        'location': meta.get('food_location', ''),
                        'image_file': meta.get('food_file', '')
                    },
                    'questions': [],
                    'question_types': []
                }
            
            # Add question information
            question_info = {
                'question_id': entry['question_id'],
                'question_type': entry['question_type'],
                'question': {
                    'chinese': entry['question'],
                    'english': entry['question_en']
                },
                'choices': {
                    'chinese': entry['choices'],
                    'english': entry['choices_en']
                },
                'answer': entry['answer']
            }
            dishes[food_name]['questions'].append(question_info)

    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: File at {file_path} is not valid JSON")
        return {}
    
    # Add question types to each dish
    for food_name in dishes:
        dishes[food_name]['question_types'] = list(question_types_per_dish[food_name])
    
    return dishes

def save_dishes(dishes: Dict, output_dir: str):
    """
    Save extracted dishes to JSON files.
    
    Args:
        dishes: Dictionary of dishes
        output_dir: Directory to save output files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save full dataset
   # with open(os.path.join(output_dir, 'dishes_full.json'), 'w', encoding='utf-8') as f:
    #    json.dump(dishes, f, ensure_ascii=False, indent=2)
    
    # Save summary
    summary = {
        'total_dishes': len(dishes),
        'dishes_by_cuisine': defaultdict(list),
        'question_type_counts': defaultdict(int)
    }
    
    for food_name, dish in dishes.items():
        cuisine = dish['metadata']['cuisine_type']
        summary['dishes_by_cuisine'][cuisine].append(food_name)
        
        for q_type in dish['question_types']:
            summary['question_type_counts'][q_type] += 1
    
    with open(os.path.join(output_dir, 'dishes_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

def main():
    # Fix the paths by using parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Configure paths relative to parent directory
    data_folder = os.path.join(parent_dir, "data_folder")
    input_file = os.path.join(data_folder, "sivqa_tidy.json")
    output_dir = os.path.join(current_dir, "extracted_dishes")
    
    print(f"Looking for file at: {input_file}")
    print(f"Current directory: {current_dir}")
    
    if not os.path.exists(input_file):
        print(f"File does not exist at {input_file}")
        return
        
    print(f"Extracting dishes from {input_file}...")
    dishes = extract_unique_dishes(input_file)
    
    if dishes:
        print(f"Found {len(dishes)} unique dishes")
        save_dishes(dishes, output_dir)
        print(f"Saved results to {output_dir}")
        
        # Print some basic statistics
        cuisines = set(dish['metadata']['cuisine_type'] for dish in dishes.values())
        print(f"\nFound dishes from {len(cuisines)} cuisine types:")
        for cuisine in sorted(cuisines):
            count = sum(1 for dish in dishes.values() if dish['metadata']['cuisine_type'] == cuisine)
            print(f"- {cuisine}: {count} dishes")
    else:
        print("No dishes were extracted. Please check the input file and try again.")

if __name__ == "__main__":
    main()