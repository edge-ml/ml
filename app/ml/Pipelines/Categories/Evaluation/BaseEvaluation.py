from app.ml.Pipelines.Categories.Classifier import BaseClassififer
from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.BaseConfig import BaseConfig
from app.DataModels.PipeLine import PipeLineStep
from typing import Optional, Tuple
from app.ml.Pipeline import Pipeline
import numpy as np

from app.ml.Pipelines.PipelineContainer import PipelineContainer

class BaseEvaluation(AbstractPipelineOption):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    # Performs evaluation using the pipeline steps and then returns the metrics and the best normalizer + classifier created during evaluation.
    def eval(self, pipeline, datasets, labelNames) -> Pipeline:
        raise NotImplementedError("Eval is not implemented")