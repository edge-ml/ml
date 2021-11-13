from models.parameter_builder import ParameterBuilder

class EdgeModel:

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
        pb.add_number("window_size", 0, 60000, False, True, 'int', True)
        return pb.parameters

    # class methods
    def __init__(self, hyperparameters):
        self.name
        self.is_fit = False
        self.hyperparameters = hyperparameters
        
    def fit(X, y):
        return
    
    def predict(X):
        return

    def compile():
        if (not self.is_fit):
            return
            # TODO: throw error
        
