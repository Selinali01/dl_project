## To do, migrate over from FoodieQA

# eval/model/base_model.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from .response_model import FoodieQAResponse

class BaseFoodieQAModel(ABC):
    """Abstract base class for FoodieQA models"""
    def __init__(self, config: Dict):
        self.config = config
        
    @abstractmethod
    async def predict(self,
        question: str,
        images: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> FoodieQAResponse:
        pass