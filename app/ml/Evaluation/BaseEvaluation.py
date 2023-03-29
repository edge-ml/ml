from app.ml.Classifier import BaseClassififer
from app.ml.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.BaseConfig import BaseConfig
from app.DataModels.PipeLine import PipeLineStep
from typing import List
from app.ml.Pipeline import Pipeline
import numpy as np

class BaseEvaluation(BaseConfig):

    def __init__(self, windower_config: PipeLineStep, featureExtractor_config: PipeLineStep, normalizer_config: PipeLineStep, classifier_config: PipeLineStep, datasets: np.ndarray, labels: List[str], evaluation_config: PipeLineStep):
        super().__init__(evaluation_config.parameters)
        self.windower_config = windower_config
        self.featureExtractor_config = featureExtractor_config
        self.normalizer_config = normalizer_config
        self.classifier_config = classifier_config
        self.datasets = datasets
        self.labels = labels

    # Performs evaluation using the pipeline steps and then returns a suitable pipline according to the strategy.
    def train_eval(self) -> Pipeline:
        raise NotImplementedError("Train eval is not implemented")
