from utils.parameter_builder import ParameterBuilder

class EdgeModel:
    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
        pb.add_number("window_size", "Window Size", "Sets the window size", 0, 60000, 100, 1, True)
        pb.add_number("sliding_step", "Sliding Step", "Sets how many steps the sliding window will slide. If it's set less than the window size, the windows will overlap.", 1, 60000, 50, 1, True)
        pb.add_selection("kernel", "Kernel", "Kernel desc", ["rbf", "linear"], "linear", False, True)
        pb.add_boolean("shrinking", "Shrinking Heuristic", "Shrinking desc", False, True)
        pb.add_selection("multi", "Multi", "", ["op1", "op2", "op3"], ["op1", "op2"], True)
        return pb.parameters

    @staticmethod
    def get_name():
        return "Edge Model Base"

    @staticmethod
    def get_description():
        return "Basic model that defines hyperparameters. Predicts random results based on class probability."

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
        
