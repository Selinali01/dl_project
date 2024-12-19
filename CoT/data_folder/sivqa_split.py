import json

def categorize_question_type(question_type):
    """
    Categorizes question types as either visual or knowledge-based
    """
    visual_types = {
        'flavor',      # Requires seeing texture, appearance
        'present',     # Requires seeing presentation style
        'main-ingredient'  # Often requires visual identification
    }
    
    knowledge_types = {
        'cuisine_type',    # Cultural knowledge
        'region-2',        # Geographic knowledge
        'cooking-skills'   # Basic cooking method knowledge
    }
    
    if question_type in visual_types:
        return 'visual'
    elif question_type in knowledge_types:
        return 'knowledge'
    else:
        return 'unknown'

def split_dataset(input_file, visual_output, knowledge_output):
    """
    Splits the SIVQA dataset into visual and knowledge-based question files
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize containers
    visual_questions = []
    knowledge_questions = []
    
    # Process each question
    for item in data:
        category = categorize_question_type(item['question_type'])
        
        if category == 'visual':
            visual_questions.append(item)
        elif category == 'knowledge':
            knowledge_questions.append(item)
    
    # Save visual questions
    with open(visual_output, 'w', encoding='utf-8') as f:
        json.dump(visual_questions, f, ensure_ascii=False, indent=4)
    
    # Save knowledge questions
    with open(knowledge_output, 'w', encoding='utf-8') as f:
        json.dump(knowledge_questions, f, ensure_ascii=False, indent=4)
    
    # Return statistics
    return {
        'total': len(data),
        'visual': len(visual_questions),
        'knowledge': len(knowledge_questions)
    }

if __name__ == "__main__":
    # File paths
    input_file = "sivqa_tidy.json"
    visual_output = "sivqa_visual.json"
    knowledge_output = "sivqa_knowledge.json"
    
    # Split the dataset and get statistics
    stats = split_dataset(input_file, visual_output, knowledge_output)
    
    # Print statistics
    print(f"Dataset splitting complete:")
    print(f"Total questions: {stats['total']}")
    print(f"Visual questions: {stats['visual']}")
    print(f"Knowledge questions: {stats['knowledge']}")
    print(f"\nFiles created:")
    print(f"- {visual_output}")
    print(f"- {knowledge_output}")