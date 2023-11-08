from app.DataModels.parameter import Parameter
from enum import Enum
from typing import List

class Platforms(Enum):
    C = "C"


class BaseConfig():

    def __init__(self, parameters : List[Parameter] = []):
        self.parameters = parameters

    @staticmethod
    def get_name():
        raise NotImplementedError()

    @staticmethod
    def get_description():
        raise NotImplementedError()

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_parameters():
        return []
    
    def persist(self):
        return {"name": self.get_name(), "parameters": self.parameters, "state": self.get_state()}
    
    def get_state(self):
        return {}

    def restore(self, config):
        self.parameters = config.parameters

    def export(self, platform: Platforms):
        if platform == Platforms.C:
            return self.exportC()

    def exportC():
        raise NotImplementedError()

    @classmethod
    def get_train_config(cls):
        return {
        "name": cls.get_name(),
        "description":  cls.get_description(),
        "parameters":  cls.get_parameters(),
        "platforms":  cls.get_platforms()
        }

    def get_param_value_by_name(self, name):
        print(self.parameters)
        for param in self.parameters:
            if param.parameter_name == name:
                return param.value
        raise KeyError(f"Parameter with name {name} not found")
        