import json
from typing import Dict, List, Union
import pandas as pd

def parse_json_lines(content: str) -> List[Dict]:
    """Parse JSON Lines format content."""
    return [json.loads(line) for line in content.split('\n') if line.strip()]

def analyze_accuracies(questions_content: str, mapping_content: str) -> pd.DataFrame:
    """
    Analyze accuracies by question type from the provided content strings.
    
    Args:
        questions_content: String containing questions data in JSON Lines format
        mapping_content: String containing question type mappings in JSON format
        
    Returns:
        pd.DataFrame: DataFrame containing accuracy statistics by question type
    """
    # Parse the mapping content
    mapping_data = json.loads(mapping_content)
    question_types = mapping_data['question_id_mappings']
    
    # Initialize statistics dictionary
    type_stats = {
        'cooking-skills': {'correct': 0, 'total': 0},
        'cuisine_type': {'correct': 0, 'total': 0},
        'flavor': {'correct': 0, 'total': 0},
        'main-ingredient': {'correct': 0, 'total': 0},
        'present': {'correct': 0, 'total': 0},
        'region-2': {'correct': 0, 'total': 0},
        'overall': {'correct': 0, 'total': 0}
    }
    
    # Process questions
    questions_data = parse_json_lines(questions_content)
    
    # Process each question
    for question in questions_data:
        qid = question['question_id']
        if qid in question_types:
            q_type = question_types[qid]
            type_stats[q_type]['total'] += 1
            type_stats[q_type]['correct'] += question['correct']
            type_stats['overall']['total'] += 1
            type_stats['overall']['correct'] += question['correct']
    
    # Calculate accuracies and create DataFrame
    results = []
    for q_type, stats in type_stats.items():
        if stats['total'] > 0:
            accuracy = (stats['correct'] / stats['total']) * 100
            results.append({
                'Question Type': q_type,
                'Total Questions': stats['total'],
                'Correct Answers': stats['correct'],
                'Accuracy (%)': round(accuracy, 2)
            })
    
    # Convert to DataFrame and sort by accuracy
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('Accuracy (%)', ascending=False)
    
    return df_results

def read_file_content(file_path: str) -> str:
    """Read file content as string."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    # Example usage with files
    questions_file = "results_template1.jsonl"  # Your questions file
    mapping_file = "question_type_analysis.json"    # Your mapping file
    
    questions_content = read_file_content(questions_file)
    mapping_content = read_file_content(mapping_file)
    
    results_df = analyze_accuracies(questions_content, mapping_content)
    
    print("\nAccuracy Analysis by Question Type:")
    print(results_df.to_string(index=False))
    
    # Optionally save to CSV
    results_df.to_csv('accuracy_results.csv', index=False)