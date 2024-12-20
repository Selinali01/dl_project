
# RAG

## Overview
We implemented RAG prompting to improve the model's reasoning capabilities on the FoodieQA dataset. 

### Implementation Details:
The RAG prompting strategy breaks down systematic steps:

1. Pass in the food name and image for each question and retrieve relevant information
2. Prompt the model with the context
4. Conclude with a final answer


## Results
### Overall Performance Improvements
| Templates | Base Prompt | Wikipedia Prompt (Improvements) | Baidu Prompt (Improvements) |
|--------|-------------|------------|-------------|
| English | 68.36% | 64.06% (-4.30% ) | - |
| Chinese | 73.05% | 79.69% (+6.64%,) | 85.16% (12.11%)|



## Key findings
An essential observation was that the inclusion of RAG context led to a general 10% increase in accuracy across most sub-question types, except for questions involving presentational aspects of dishes. This demonstrates the model’s improved ability to handle diverse queries when supported by rich contextual information.

Observations and Recommendations

The disparity between English and Chinese performance highlights the necessity of localized data sources. The limited coverage of English Wikipedia proved to be a bottleneck.Utilizing Baidu for the Chinese RAG pipeline for high quality domain-specific data has indeed significantly outperformed Wikipedia.

Our findings illustrate the transformative potential of RAG in improving FoodieQA task performance, especially for region-specific queries.



## Instructions to replicate results

### Evaluation scripts
- See evaluation scripts in `model-eval/scripts/`
- See example bash file in `model-eval/run`

###  Steps:
- Set up
    ```
    conda create -n foodie python=3.9
    pip install -r requirements.txt
    ```

- Download datset from Huggingface and add to data_folder/images

```
lyan62/FoodieQA
```

- Add gpt4o key in .env
    ```
    OPENAI_API_KEY =''
    ```

- Replicate single-image VQA Results:

    ```
        python model-eval/scripts/gpt4osivqa.py 
        --data_dir <data_folder> --output_dir <out_folder> --eval_file <evaluation_file> 
    ```
     - We used template 1 for the base template (best performing out of the FoodieQA options), and template 5 for Wikipedia results, template 6 for Baidu Results.
