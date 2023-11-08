from app.ml.BaseConfig import BaseConfig
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.Pipelines.PipelineContainer import PipelineContainer


class BaseNormalizer(AbstractPipelineOption):
    
    def __init__(self, parameters=...):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        raise NotImplementedError()
    
    def fit_normalize(self, data):
        raise NotImplementedError()

    def normalize(self, data):
        raise NotImplementedError()
    
    def exec(self, data : PipelineContainer) -> PipelineContainer:
        return PipelineContainer(self.normalize(data.data), data.labels, data.meta)
    
    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        output = self.fit_normalize(data.data)
        self.input_shape = data.data.shape
        self.output_shape = output.shape
        return PipelineContainer(output, data.labels, data.meta)