from enum import Enum
from typing import List
from ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from ml.Pipelines.Abstract.StepType import StepType
    
class AbstractPipelineStep():
    def __init__(self, name, description, options, type: StepType = StepType.CORE):
        self.name = name
        self.description = description
        self.options = options
        for option in self.options:
            option.type = type
        self.type = type

    def get_train_config(self):
        return {"name": self.name, "description": self.description, "type": self.type, "options": [x.get_train_config() for x in self.options]}