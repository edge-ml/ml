from app.ml.Pipelines.Categories.Classifier import BaseClassififer
from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.BaseConfig import BaseConfig
from app.DataModels.PipeLine import PipeLineStep
from typing import Optional, Tuple
from app.ml.Pipeline import Pipeline
import numpy as np

class BaseEvaluation(BaseConfig):

    def __init__(self, normalizer_config: PipeLineStep, classifier_config: PipeLineStep, evaluation_config: PipeLineStep):
        super().__init__(evaluation_config.parameters)
        self.normalizer_config = normalizer_config
        self.classifier_config = classifier_config

    # Performs evaluation using the pipeline steps and then returns the metrics and the best normalizer + classifier created during evaluation.
    def eval(self, X, Y, labels) -> Tuple[dict, Tuple[Optional[BaseNormalizer], Optional[BaseClassififer]]]:
        raise NotImplementedError("Eval is not implemented")
