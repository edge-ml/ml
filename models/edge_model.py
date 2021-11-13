from models.parameter_builder import ParameterBuilder

class EdgeModel:
    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
        pb.add_number("window_size", 0, 60000, 100, False, True, 'int', True)
        return pb.parameters

    # class methods
    def __init__(self, hyperparameters):
        self.name
        self.is_fit = False
        self.hyperparameters = hyperparameters
        
    def fit(self, X_train, y_train):
        return True
    
    def predict(self, X_test, y_test):
        labels = ['a', 'b']
        confusion_matrix = [[5,0],[0,5]]
        return (labels, confusion_matrix)

    def compile(self):
        if (not self.is_fit):
            return
            # TODO: throw error
        
