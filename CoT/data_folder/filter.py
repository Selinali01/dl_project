import json

def filter_cuisine_questions():
    # Read the original JSON file
    with open('sivqa_tidy.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Filter questions where question_type is "cuisine_type"
    cuisine_questions = [item for item in data if item['question_type'] == 'cuisine_type']
    
    # Write the filtered data to a new file
    with open('sivqa_cuisine.json', 'w', encoding='utf-8') as file:
        json.dump(cuisine_questions, file, ensure_ascii=False, indent=4)
    
    print(f"Original file had {len(data)} questions")
    print(f"Filtered file has {len(cuisine_questions)} cuisine type questions")
    print("Filtered data has been saved to 'sivqa_cuisine.json'")

if __name__ == "__main__":
    filter_cuisine_questions()