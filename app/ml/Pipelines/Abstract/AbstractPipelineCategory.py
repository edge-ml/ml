from enum import Enum


class PipelineCategoryType(Enum):
    CORE = 1
    INFO = 2
    eval = 3
    PRE = 4

class AbstractPipelineCategory():
    
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
    def __init__(self, name, description, options, type: PipelineCategoryType = PipelineCategoryType.CORE):
        self.name = name
        self.description = description
        self.options = options
        self.type = type