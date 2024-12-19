# Chain of Thought

## Overview
We implemented Chain of Thought (CoT) prompting to improve the model's visual reasoning capabilities on the FoodieQA dataset. Our approach focuses on structured analysis of visual elements in Chinese dishes, with particular emphasis on flavor identification, presentation evaluation, and ingredient recognition.

### Implementation Details:
The CoT prompting strategy breaks down visual analysis into systematic steps:

1. List all visible ingredients and components in the dish
2. Analyze each option step-by-step
3. Provide explicit reasoning
4. Conclude with a final answer


## Results
### Overall Performance Improvements
| Metric | Base Prompt | CoT Prompt | Improvement |
|--------|-------------|------------|-------------|
| Overall Accuracy | 58.57% | 64.29% | +5.72% |
| Flavor Recognition | 60.87% | 60.87% | 0% |
| Presentation Analysis | 64.29% | 78.57% | +14.28% |
| Main Ingredient Identification | 40.00% | 60.00% | +20.00% |

### Performance by Question Type
| Question Category | Total Questions | Correct Answers | Accuracy |
|------------------|-----------------|-----------------|-----------|
| Overall | 70 | 45 | 64.29% |
| Flavor | 46 | 28 | 60.87% |
| Presentation | 14 | 11 | 78.57% |
| Main Ingredient | 10 | 6 | 60.00% |


## Key findings
- Most significant improvements seen in presentation analysis (+14.28%) and main ingredient identification (+20.00%)
- Structured reasoning particularly effective for visual-based questions
- CoT prompting helps distinguish between similar attributes (e.g., texture vs. flavor)


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

- Add gpt4o key in .env
    ```
    OPENAI_API_KEY =''
    ```

- Replicate single-image VQA Results:

    ```
        python model-eval/scripts/gpt4osivqa.py 
        --data_dir <data_folder> --output_dir <out_folder> --eval_file <evaluation_file> 
    ```
     - We used template 1 for the base template (best performing out of the FoodieQA options), and template 14 for the CoT results

    - For the data, use sivqa_visual.json to run on only the visual questions and reproduce our results

    