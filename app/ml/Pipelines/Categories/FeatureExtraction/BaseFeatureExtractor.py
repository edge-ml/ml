from app.ml.Pipelines.Categories.FeatureExtraction import BaseFeatureExtractor
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption

class BaseFeatureExtractor(AbstractPipelineOption):

    def __init__(self, parameters):
        super().__init__(parameters)

    def extract_features(self):
        raise NotImplementedError()