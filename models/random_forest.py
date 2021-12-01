from models.parameter_builder import ParameterBuilder
from models.edge_model import EdgeModel

class RandomForest(EdgeModel):
    pass

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder(EdgeModel.get_hyperparameters()) #get base parameter

        return pb.parameters

    @staticmethod
    def get_name():
        return "Random Forest Classifier"

    @staticmethod
    def get_description():
        return "A simple random forest classifier."

    # class methods
    def __init__(self, hyperparameters):
        super(hyperparameters)
        
    def fit(X_train, y_train):
        return True
    
    def predict(self, X_test, y_test):
        labels = ['a', 'b']
        confusion_matrix = [[5,0],[0,5]]
        return (labels, confusion_matrix)

    def compile(self):
        if (not self.is_fit):
            return
            # TODO: throw error
        
