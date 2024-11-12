# eval/tests/create_sichuan_test.py
from pathlib import Path
import json
import sys
import os

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from eval.model.enums import TaskType

def create_sichuan_test():
    """Create test case for Sichuan cold dish example"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Create full directory path relative to project root
    test_dir = project_root / 'eval' / 'tests' / 'sichuan_dishes' / 'test1'
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create images directory
    image_dir = test_dir / 'images'
    image_dir.mkdir(exist_ok=True)
    
    # Create test case JSON
    test_data = {
        "id": "sichuan_dishes/test1",
        "question": "哪一道菜属于川菜中的凉菜？Which is a cold dish in Sichuan cuisine?",
        "task_type": TaskType.MIVQA.value,
        "image_paths": [
            "images/A.jpg",
            "images/B.jpg",
            "images/C.jpg",
            "images/D.jpg"
        ],
        "ground_truth": "C",  # Assuming B is the correct cold dish
        "context_info": {
            "cuisine_type": "sichuan",
            "dish_type": "cold_dish",
            "language": "zh-en",
            "ground_truth": "B"  # Added for mock model
        }
    }
    
    # Save test.json
    json_path = test_dir / "test.json"
    print(f"Creating test.json at: {json_path}")
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"Test file created at: {json_path}")
    print(f"Please place your images in: {image_dir}")
    print("Required image names:")
    for img in ["A.jpg", "B.jpg", "C.jpg", "D.jpg"]:
        print(f"  - {img}")

if __name__ == "__main__":
    create_sichuan_test()