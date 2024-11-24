import json
from collections import defaultdict
from datetime import datetime

def analyze_performance_by_question_type():
    # Load question type mappings
    with open('question_type_analysis.json', 'r', encoding='utf-8') as f:
        type_data = json.load(f)
        question_types = type_data['question_id_mappings']

    # Initialize counters for each question type
    type_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    # Process results file
    with open('results_template5_zh.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line)
            question_id = result['question_id']
            
            # Get question type for this question
            if question_id in question_types:
                q_type = question_types[question_id]
                type_stats[q_type]['total'] += 1
                type_stats[q_type]['correct'] += result['correct']

    # Calculate performance metrics
    performance_analysis = {
        "analysis_timestamp": datetime.now().isoformat(),
        "performance_by_type": {},
        "overall_performance": {
            "total_questions": 0,
            "total_correct": 0
        }
    }

    for q_type, stats in type_stats.items():
        if stats['total'] > 0:
            accuracy = (stats['correct'] / stats['total']) * 100
            performance_analysis["performance_by_type"][q_type] = {
                "total_questions": stats['total'],
                "correct_answers": stats['correct'],
                "accuracy": round(accuracy, 2),
            }
            performance_analysis["overall_performance"]["total_questions"] += stats['total']
            performance_analysis["overall_performance"]["total_correct"] += stats['correct']

    # Calculate overall accuracy
    total_accuracy = (performance_analysis["overall_performance"]["total_correct"] / 
                     performance_analysis["overall_performance"]["total_questions"]) * 100
    performance_analysis["overall_performance"]["accuracy"] = round(total_accuracy, 2)

    # Sort types by accuracy to identify struggling areas
    sorted_performance = sorted(
        performance_analysis["performance_by_type"].items(),
        key=lambda x: x[1]["accuracy"]
    )

    # Add sorted performance summary
    performance_analysis["performance_summary"] = {
        "best_performing_type": sorted_performance[-1][0],
        "worst_performing_type": sorted_performance[0][0],
        "performance_ranking": [
            {
                "type": q_type,
                "accuracy": stats["accuracy"],
                "total_questions": stats["total_questions"],
                "correct_answers": stats["correct_answers"]
            }
            for q_type, stats in sorted_performance
        ]
    }

    # Save results
    with open('performance_analysis_5_zh.json', 'w', encoding='utf-8') as f:
        json.dump(performance_analysis, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\nPerformance Analysis Summary:")
    print("=" * 40)
    print(f"Overall Accuracy: {total_accuracy:.2f}%")
    print("\nAccuracy by Question Type (Sorted from Worst to Best):")
    print("-" * 40)
    for q_type, stats in sorted_performance:
        print(f"{q_type:15} {stats['accuracy']:6.2f}% ({stats['correct_answers']}/{stats['total_questions']})")

if __name__ == "__main__":
    analyze_performance_by_question_type()