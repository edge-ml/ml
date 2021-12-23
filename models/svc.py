from utils.parameter_builder import ParameterBuilder
from models.edge_model import EdgeModel
import copy


class SVC(EdgeModel):
    pass

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter
        return pb.parameters

    @staticmethod
    def get_name():
        return "SVC Classifier"

    @staticmethod
    def get_description():
        return "A simple SVC classifier."

    # class methods
    def __init__(self, hyperparameters):
        super(hyperparameters)

    def fit(X_train, y_train):
        return True

    def predict(self, X_test, y_test):
        labels = ["a", "b"]
        confusion_matrix = [[5, 0], [0, 5]]
        return (labels, confusion_matrix)

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
