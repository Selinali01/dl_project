from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from pathlib import Path
from .model.enums import ModelArchitecture, TaskType
from .model.response_model import FoodieQAResponse
from .model.base_model import BaseModel

@dataclass 
class ExperimentConfig:
    """Configuration for running FoodieQA experiments"""
    name: str
    architecture: ModelArchitecture
    task_type: TaskType
    model_config: Dict
    test_files: List[str]
    language: str
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "architecture": self.architecture.value,
            "task_type": self.task_type.value,
            "model_config": self.model_config,
            "test_files": self.test_files,
            "language": self.language
        }

@dataclass
class TestCase:
    """Schema for a single test case"""
    id: str
    question: str
    task_type: TaskType
    image_paths: Optional[List[str]]
    ground_truth: str
    context_info: Optional[Dict] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TestCase":
        return cls(
            id=data["id"],
            question=data["question"],
            task_type=TaskType(data["task_type"]),
            image_paths=data.get("image_paths"),
            ground_truth=data["ground_truth"],
            context_info=data.get("context_info")
        )

@dataclass
class TestResult:
    """Schema for a single test result"""
    test_case_id: str
    predicted: FoodieQAResponse
    accuracy: float
    error_analysis: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "test_case_id": self.test_case_id,
            "predicted": self.predicted.__dict__,
            "accuracy": self.accuracy,
            "error_analysis": self.error_analysis
        }

@dataclass
class ExperimentResult:
    """Schema for experiment results"""
    experiment_name: str
    model_architecture: str
    task_type: str
    model_config: Dict
    language: str
    timestamp: str
    test_results: List[TestResult]
    aggregate_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return {
            "experiment_name": self.experiment_name,
            "model_architecture": self.model_architecture,
            "task_type": self.task_type,
            "model_config": self.model_config,
            "language": self.language,
            "timestamp": self.timestamp,
            "test_results": [r.to_dict() for r in self.test_results],  
            "aggregate_metrics": self.aggregate_metrics
        }

def evaluate_prediction(prediction: str, ground_truth: str) -> float:
    """
    Simple accuracy evaluation - exact match
    Returns 1.0 if prediction matches ground truth, 0.0 otherwise
    """
    return float(prediction.lower().strip() == ground_truth.lower().strip())

def create_test_file(test_case: TestCase) -> None:
    """Create a test case JSON file"""
    test_dir = Path(f"tests/{test_case.id}")
    test_dir.mkdir(exist_ok=True)
    filepath = test_dir / "test.json"
    
    test_data = {
        "id": test_case.id,
        "question": test_case.question,
        "task_type": test_case.task_type.value,
        "image_paths": test_case.image_paths,
        "ground_truth": test_case.ground_truth,
        "context_info": test_case.context_info
    }
    
    with open(filepath, "w") as f:
        json.dump(test_data, f, indent=2)

async def run_experiment(
    config: ExperimentConfig,
    model: BaseModel,
    output_dir: str = "results"
) -> None:
    """Run experiment and save results"""
    os.makedirs(output_dir, exist_ok=True)
    test_results = []
    test_dir = Path("tests")
    
    # Run tests
    for test_file in config.test_files:
        with open(test_dir / test_file / "test.json", "r") as f:
            test_case = TestCase.from_dict(json.load(f))
            
        # Load images if needed
        images = None
        if test_case.image_paths:
            images = [str(test_dir / test_file / img_path) 
                     for img_path in test_case.image_paths]
            
        # Get prediction
        prediction = await model.predict(
            question=test_case.question,
            images=images,
            context=test_case.context_info
        )
        
        # Evaluate
        accuracy = evaluate_prediction(prediction.answer, test_case.ground_truth)
        
        # Store result
        test_results.append(TestResult(
            test_case_id=test_case.id,
            predicted=prediction,
            accuracy=accuracy
        ))
    
    # Compute aggregate metrics
    avg_accuracy = sum(r.accuracy for r in test_results) / len(test_results)
    
    # Create experiment result
    result = ExperimentResult(
        experiment_name=config.name,
        model_architecture=config.architecture.value,
        task_type=config.task_type.value,
        model_config=config.model_config,
        language=config.language,
        timestamp=datetime.now().isoformat(),
        test_results=test_results,
        aggregate_metrics={"accuracy": round(avg_accuracy * 100, 2)}
    )
    
    # Save results
    output_path = Path(output_dir) / f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)