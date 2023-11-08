
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.BaseConfig import BaseConfig
from app.ml.Pipelines.PipelineContainer import PipelineContainer

class BaseClassififer(AbstractPipelineOption):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.is_fit = False
        self.parameters = parameters


    def fit(self, X_train, y_train):
        raise NotImplementedError

    def predict(self, X_test):
        raise NotImplementedError
    
    def exec(self, data: PipelineContainer) -> PipelineContainer:
        return PipelineContainer(self.predict(data.data), data.labels, data.meta)
    
    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        print("0" * 30)
        print("BaseClassifier")
        print(data.data.shape)

        self.fit(data.data, data.labels)
        output = self.predict(data.data)
        self.input_shape = data.data.shape
        self.output_shape = output.shape
        return PipelineContainer(output, data.labels, data.meta)