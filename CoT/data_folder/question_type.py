import json
from collections import Counter
from datetime import datetime

def analyze_question_types(json_path):
    # Read JSON file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_path}")
        return None
    
    # Create mappings and counters
    question_id_to_type = {}
    type_counter = Counter()
    
    # Process each question
    for item in data:
        question_id = item['question_id']
        question_type = item['question_type']
        
        # Map question ID to type
        question_id_to_type[question_id] = question_type
        
        # Count question types
        type_counter[question_type] += 1
    
    # Calculate percentages
    total_questions = sum(type_counter.values())
    type_statistics = {}
    
    for qtype, count in sorted(type_counter.items()):
        percentage = (count / total_questions) * 100
        type_statistics[qtype] = {
            "count": count,
            "percentage": round(percentage, 1)
        }
    
    # Prepare results dictionary
    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_questions": total_questions,
        "question_id_mappings": question_id_to_type,
        "question_type_statistics": type_statistics
    }
    
    return results

def save_results(results, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results successfully saved to {output_path}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def main():
    # Specify your input and output JSON file paths
    input_path = 'sivqa_tidy.json'
    output_path = 'question_type_analysis.json'
    
    # Run analysis
    results = analyze_question_types(input_path)
    
    if results:
        # Save results to JSON file
        save_results(results, output_path)

if __name__ == "__main__":
    main()