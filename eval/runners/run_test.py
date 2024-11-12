# eval/runners/run_test.py
import asyncio
from ..model.enums import ModelArchitecture, TaskType
from ..model.mock_model import MockFoodieQAModel
from ..foodieqa_test import ExperimentConfig, run_experiment

async def test_sichuan_example():
    config = ExperimentConfig(
        name="sichuan_test",
        architecture=ModelArchitecture.BASE,
        task_type=TaskType.MIVQA,
        model_config={
            "task_type": "mivqa",
            "model_name": "mock-foodieqa"
        },
        test_files=["eval/tests/sichuan_dishes/test1"],
        language="zh"
    )
    
    model = MockFoodieQAModel(config.model_config)
    await run_experiment(config, model, output_dir="results")

if __name__ == "__main__":
    asyncio.run(test_sichuan_example())