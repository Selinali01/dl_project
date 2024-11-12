import asyncio
from pathlib import Path
from ..model.enums import ModelArchitecture, TaskType
from ..model.mock_model import MockFoodieQAModel
from ..foodieqa_test import ExperimentConfig, run_experiment
from ..tests.create_mock_tests import create_mock_test_cases

async def run_mock_evaluation():
    """Run evaluation with mock model for testing"""
    # Create mock test cases
    create_mock_test_cases()
    
    config = ExperimentConfig(
        name="mock_test_run",
        architecture=ModelArchitecture.BASE,
        task_type=TaskType.MIVQA,
        model_config={
            "task_type": "mivqa",
            "model_name": "mock-foodieqa"
        },
        test_files=["mock_mivqa_1", "mock_sivqa_1", "mock_textqa_1"],
        language="zh"
    )
    
    model = MockFoodieQAModel(config.model_config)
    await run_experiment(config, model, output_dir="results")

if __name__ == "__main__":
    asyncio.run(run_mock_evaluation())
