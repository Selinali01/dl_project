from typing import List, Dict, Optional
import random
from .base_model import BaseFoodieQAModel
from .response_model import FoodieQAResponse

class MockFoodieQAModel(BaseFoodieQAModel):
    """Mock model for testing the evaluation pipeline"""
    def __init__(self, config: Dict):
        super().__init__(config)
        # Simulate different accuracies for different tasks
        self.mock_accuracies = {
            "mivqa": 0.45,  # Similar to Idefics2-8B performance
            "sivqa": 0.50,  # Similar to Yi-VL performance
            "textqa": 0.40  # Similar to baseline performance
        }
        
    async def predict(self,
        question: str,
        images: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> FoodieQAResponse:
        # Simulate model prediction
        # In real FoodieQA, answers are A/B/C/D for VQA tasks
        possible_answers = ["A", "B", "C", "D"]
        
        # Randomly select answer based on mock accuracy
        task_type = self.config.get("task_type", "mivqa")
        accuracy = self.mock_accuracies[task_type]
        
        if random.random() < accuracy:
            # Simulate correct answer
            answer = context.get("ground_truth") if context else random.choice(possible_answers)
        else:
            # Simulate incorrect answer
            wrong_answers = [a for a in possible_answers if a != context.get("ground_truth")]
            answer = random.choice(wrong_answers)
            
        return FoodieQAResponse(
            answer=answer,
            confidence=random.uniform(0.6, 0.9)
        )