# RAG + CoT


## Overview
We implemented RAG and CoT prompting to improve the model's contextual and visual reasoning capabilities on the FoodieQA dataset.


## Experiment 1:
### Implementation Details:
The RAG amd CoT prompting strategy breaks down systematic steps:
1. Predicting top 3 dishes in image with CoT
2. Retrieve relevant context for 3 dishes in database
3. Prompt the model with the context + full reasoning from CoT


## Results
### Overall Performance Improvements
| Templates | Base Prompt | Wikipedia + Baidu Prompt (Improvements) | Baidu Prompt (Improvements) |
|--------|-------------|------------|-------------|
| Chinese | 60.94% | 60.55% (-0.39%,) | 61.33% (+0.39%)|




## Experiment 2:
### Implementation Details:
1. Predicting top 3 dishes in image with CoT
2. Identify the question type for each question_id
2. If question is knowledge type, then RAG prompting with context for the 3 dishes in Baidu database (Template 100)
4. If question is visual type, then use CoT prompting (Template 11)




## Results
### Overall Performance Improvements
| Metric | Base Prompt | CoT + RAG Prompt | Improvement |
|--------|-------------|------------|-------------|
| Overall Accuracy | 60.94% | 63.28% | +2.34% |
| Main Ingredient Identification | 60.00% | 50.00% | -10.00% |
| Cooking Skills Recognition | 70.59% | 62.75 | -7.84% |
| Cuisine Type Identification | 61.43% | 58.57 | -2.86% |
| Presentation Analysis | 78.57% | 78.57% | +0% |
| Flavor Recognition | 63.04% | 65.22% | 2.18% |
| Region identification | 47.69% | 66.15% | +18.46% |






## Key findings
The presentation sub-question type maintained its 78.57% accuracy from the baseline setup. While knowledge questions like region-2 maintained a higher accuracy compared to the baseline
The results underline the importance of tailoring data pipelines to the specific requirements of each question type.






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


- Download dataset from Huggingface and add to data_folder/images


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
     - We used template 100 for CoT dish identification + RAG, template 11 for CoT dish identification + CoT.
