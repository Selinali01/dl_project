# Enhancing Vision-Language Models for Fine-Grained Cultural Understanding

This repository contains the implementation of our research on improving vision-language models' understanding of culturally nuanced content, using Chinese cuisine as a case study. We explore the combination of Retrieval-Augmented Generation (RAG) and Chain-of-Thought (CoT) prompting to enhance model performance on the FoodieQA dataset.

## Repository Structure
This repository is organized into multiple branches, each focusing on different aspects of the implementation:

```
dl_project/
├── README.md
├── requirements.txt
├── FoodieQA/               # Original FoodieQA implementation
│   └── [Original files]
│
├── RAG/                    # RAG implementation
│   ├── README.md           # README for RAG results and replication instructions
│   ├── model-eval          
│   └── output                 
│
├── CoT/                    # Chain of Thought implementation
│   ├── README.md           # README for CoT results and replication instructions
│   ├── model-eval          
│   └── output     
│
├── RAG_CoT/               # Combined implementation
│   ├── README.md          # README for CoT + RAG combined approach results and replication instructions
│   ├── model-eval          
│   └── output    
└── 
```

## Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/Selinali01/dl_project.git
cd dl_project
```
2. Download datset from Huggingface and add to data_folder
```
lyan62/FoodieQA
```

3. Choose the desired branch
```bash
# For RAG implementation
git checkout RAG

# For CoT implementation
git checkout CoT

# For combined RAG+CoT implementation
git checkout RAG_CoT
```

4. Install requirements
```bash
pip install -r requirements.txt
```

## Key Features
1. RAG Implementation
- Comprehensive knowledge base incorporating Wikipedia and Baidu data
- Efficient vector database for knowledge retrieval
- Custom prompting templates integrating retrieved context

2. CoT Implementation
- Structured prompting for enhanced visual reasoning
- Step-by-step analysis of visual features
- Improved logical consistency in responses

3. Hybrid Approach (RAG+CoT)
- Adaptive template selection based on question type
- Combined knowledge retrieval and reasoning
- Optimized performance across diverse query types