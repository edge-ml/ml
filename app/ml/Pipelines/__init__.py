from typing import List

from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator
from app.ml.Pipelines.AutoMLClassificationPipeline import AutoMLClassificationPipeline
from app.ml.Pipelines.ManualClassificationPipeline import ManualClassificationPipeline

_pipelines : List[AbstractPipeLineCreator] = [ManualClassificationPipeline, AutoMLClassificationPipeline]


def get_configs():
    return [x.get_train_config() for x in _pipelines]

PIPELINES_CONFIG = get_configs()