from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class FoodieQAResponse:
    """Schema for model response"""
    answer: str
    confidence: float
    supporting_info: Optional[Dict] = None