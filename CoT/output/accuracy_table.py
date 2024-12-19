import json
from typing import Dict, List
import pandas as pd

def analyze_accuracies(question_file: str, type_mapping_file: str) -> pd.DataFrame:
    """
    Analyze accuracies by question type from the provided files.
    
    Args:
        question_file: Path to the JSON file containing questions and responses
        type_mapping_file: Path to the JSON file containing question type mappings
        
    Returns:
        pd.DataFrame: DataFrame containing accuracy statistics by question type
    """
    # Read the type mappings
    with open(type_mapping_file, 'r', encoding='utf-8') as f:
        type_data = json.load(f)
    question_types = type_data['question_id_mappings']
    
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
    
    # Process the questions file
    with open(question_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                question_data = json.loads(line)
                qid = question_data['question_id']
                
                if qid in question_types:
                    q_type = question_types[qid]
                    type_stats[q_type]['total'] += 1
                    type_stats[q_type]['correct'] += question_data['correct']
                    type_stats['overall']['total'] += 1
                    type_stats['overall']['correct'] += question_data['correct']
    
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

if __name__ == "__main__":
    # Example usage
    question_file = "results_template1_verbose.jsonl"  # Your input file with questions
    type_mapping_file = "question_type_analysis.json"  # Your mapping file
    
    results_df = analyze_accuracies(question_file, type_mapping_file)
    print("\nAccuracy Analysis by Question Type:")
    print(results_df.to_string(index=False))