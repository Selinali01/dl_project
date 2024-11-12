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