import asyncio
from pathlib import Path
from ..model.enums import ModelArchitecture, TaskType
from ..foodieqa_test import ExperimentConfig, run_experiment

async def run_foodieqa_evaluation(model_name: str = "idefics2-8b"):
    """Run evaluation with actual FoodieQA model"""
    # Example configuration for FoodieQA dataset
    config = ExperimentConfig(
        name=f"foodieqa_{model_name}",
        architecture=ModelArchitecture.BASE,
        task_type=TaskType.MIVQA,
        model_config={
            "model_name": model_name,
            "task_type": "mivqa",
        },
        test_files=[
            "dim_sum/test1",
            "hot_pot/test1",
            "noodles/test1",
            # Add more test cases
        ],
        language="zh"
    )
    
    # Import once FoodiQA is set up
    # from ..model.foodieqa_model import FoodieQAModel
    # model = FoodieQAModel(config.model_config)
    
    await run_experiment(config, model, output_dir="results")

if __name__ == "__main__":
    asyncio.run(run_foodieqa_evaluation())