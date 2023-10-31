

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
    def __init__(self, name, description, options):
        self.name = name
        self.description = description
        self.options = options