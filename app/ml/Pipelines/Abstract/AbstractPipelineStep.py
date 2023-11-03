from enum import Enum


class StepType(Enum):
    CORE = "CORE"
    INFO = "INFO"
    EVAL = "EVAL"
    PRE = "PRE"

class AbstractPipelineStep():
    
    @staticmethod
    def get_steps():
        return []
    
    @staticmethod
    def get_name():
        raise NotImplementedError()
    
    @staticmethod
    def get_description():
        raise NotImplementedError()
    
class PipelineCategory():
    def __init__(self, name, description, options, type: StepType = StepType.CORE):
        self.name = name
        self.description = description
        self.options = options
        self.type = type