from app.ml.Pipelines.Categories.FeatureExtraction import BaseFeatureExtractor
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.Pipelines.PipelineContainer import PipelineContainer

class BaseFeatureExtractor(AbstractPipelineOption):

    def __init__(self, parameters):
        super().__init__(parameters)

    def extract_features(self, windows):
        raise NotImplementedError()
    
    def exec(self, data: PipelineContainer) -> PipelineContainer:
        return PipelineContainer(self.extract_features(data.data), data.labels, data.meta)
    
    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        return PipelineContainer(self.extract_features(data.data), data.labels, data.meta)
