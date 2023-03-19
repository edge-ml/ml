
class Normalizer():
    
    def __init__(self, parameters):
        self.parameters = parameters

    @staticmethod
    def get_name():
        raise NotImplementedError()

    @staticmethod
    def config():
        raise NotImplementedError()
    
    def fit_normalize(self, data):
        raise NotImplementedError()

    def normalize(self, data):
        raise NotImplementedError()
    
    def get_state(self):
        raise NotImplementedError()