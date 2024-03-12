from ml.Pipelines import ManualClassificationPipeline
from DataModels.api import PipelineModel


def test_config_parsing_automl():
    config = ManualClassificationPipeline.get_train_config()
    PipelineModel.model_validate(config)
    