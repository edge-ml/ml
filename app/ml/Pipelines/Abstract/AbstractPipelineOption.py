from typing import List
from DataModels.parameter import Parameter
from ml.Pipelines.PipelineContainer import PipelineContainer
from utils.enums import Platforms

class AbstractPipelineOption():

    def __init__(self, parameters : List[Parameter] = []):
        self.parameters = parameters
        self.input_shape = None
        self.output_shape = None
        type = None

    @staticmethod
    def get_name():
        raise NotImplementedError()

    @staticmethod
    def get_description():
        raise NotImplementedError()
    
    @staticmethod
    def get_parameters():
        return []
    
    @staticmethod
    def get_platforms():
        return []
    
    def fit_exec(self, data : PipelineContainer) -> PipelineContainer:
        raise NotImplementedError()
    
    def exec(self, data : PipelineContainer) -> PipelineContainer:
        raise NotImplementedError()

    def persist(self):
        return {"name": self.get_name(), "description": self.get_description(), "parameters": self.parameters, "state": self.get_state(), "input_shape": self.input_shape, "output_shape": self.output_shape}
    
    def get_state(self):
        return {}
    
    def as_file(self):
        raise NotImplementedError()

    def restore(self, config):
        print("Restore:", self.get_name(), config.input_shape)
        self.parameters = config.parameters
        self.input_shape = config.input_shape
        self.output_shape = config.output_shape

    def export(self, params, platform: Platforms):
        return self.exportC(params)

    def exportC(params):
        raise NotImplementedError()
    
    @classmethod
    def get_train_config(cls):
        return {
        "name": cls.get_name(),
        "description":  cls.get_description(),
        "parameters":  cls.get_parameters(),
        "platforms":  cls.get_platforms(),
        "type": cls.type
        }

    def get_param_value_by_name(self, name):
        print(self.parameters)
        for param in self.parameters:
            if param.parameter_name == name:
                return param.value
        raise KeyError(f"Parameter with name {name} not found")