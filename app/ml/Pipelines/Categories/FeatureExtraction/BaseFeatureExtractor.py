from app.ml.Pipelines.Categories.FeatureExtraction import BaseFeatureExtractor
from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep

class BaseFeatureExtractor(AbstractPipelineStep):

    def __init__(self, parameters):
        super().__init__(parameters)

    def extract_features(self):
        raise NotImplementedError()