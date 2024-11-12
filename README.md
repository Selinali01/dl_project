# Project Structure

```
eval/
├── __init__.py
├── foodieqa_test.py        # Main evaluation logic
├── examples/               # Example test cases
├── results/               # Experiment results
├── tests/                 # Test cases
│   ├── test1/
│   │   ├── test.json
│   │   └── images/
│   └── test2/
│       ├── test.json
│       └── images/
└── model/
    ├── __init__.py
    ├── enums.py           # Enums for model types and tasks
    ├── builder.py         # Model factory
    ├── base_model.py      # Base model interface
    ├── rag_model.py       # RAG implementation
    └── response_model.py  # Response schemas
```

## Directory Overview

### Core Files
- `foodieqa_test.py`: Contains the main evaluation pipeline and experiment running logic
- `model/base_model.py`: Implementation of the original FoodieQA model
- `model/rag_model.py`: RAG-enhanced version of FoodieQA
- `model/response_model.py`: Data structures for model responses

### Data Directories
- `examples/`: Contains example test cases and usage demonstrations
- `results/`: Stores experiment results and performance metrics
- `tests/`: Contains test cases with questions and images

### Support Files
- `model/enums.py`: Enumerations for model types and tasks
- `model/builder.py`: Factory class for creating model instances