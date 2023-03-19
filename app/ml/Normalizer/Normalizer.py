
class Normalizer():
    
    def __init__(self, parameters):
        self.parameters = parameters

    @staticmethod
    def get_name():
        raise NotImplementedError()

    def normalize(self, data):
        raise NotImplementedError()

    def normalize_with(self, data, settings):
        raise NotImplementedError()