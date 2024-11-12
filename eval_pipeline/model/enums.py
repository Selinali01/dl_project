from enum import Enum

class ModelArchitecture(Enum):
    BASE = "base"
    RAG = "rag"
    
class TaskType(Enum):
    MIVQA = "mivqa"
    SIVQA = "sivqa"
    TEXTQA = "textqa"