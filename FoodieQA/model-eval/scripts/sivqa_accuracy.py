import json
from sklearn.metrics import accuracy_score

# Paths to the JSON files
ground_truth_file = "FoodieQA\\data_folder\\sivqa_tidy.json"
predictions_file = "FoodieQA\output\sivqa_gpt-4o-mini_prompt0_zh.jsonl"
ans_map = {"A": "1", "B": "2", "C": "3", "D": "4"}


# Load ground truth data
def load_ground_truth(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load predictions data
def load_predictions(file_path):
    predictions = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            predictions.append(json.loads(line))
    # print(predictions)
    return predictions
# Parse predictions
def parse_predictions(predictions):
    parsed_predictions = []
    for prediction in predictions:
        # Extract answer letter from the response
        response_text = prediction["response"][0]  # Assuming response is a list
        answer_letter = response_text.strip().split()[-1]  # Extract the last word
        # Map letter to number
        answer_number = ans_map.get(answer_letter, "N/A")
        parsed_predictions.append(answer_number)
    return parsed_predictions

# Match predictions with ground truth
def calculate_accuracy(ground_truth, predictions):
    ground_truth_answers = [q["answer"] for q in ground_truth]
    prediction_answers = [
        predictions[idx] if idx < len(predictions) else "N/A" 
        for idx in range(len(ground_truth_answers))
    ]
    return accuracy_score(ground_truth_answers, prediction_answers)

# Main logic
if __name__ == "__main__":
    ground_truth_data = load_ground_truth(ground_truth_file)
    predictions_data = load_predictions(predictions_file)
    
    # Parse predictions to match answer format
    parsed_predictions = parse_predictions(predictions_data)

    # Calculate accuracy
    accuracy = calculate_accuracy(ground_truth_data, parsed_predictions)
    print(f"Accuracy: {accuracy:.4f}")
