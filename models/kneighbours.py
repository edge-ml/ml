from utils.parameter_builder import ParameterBuilder
from models.edge_model import EdgeModel
import copy


class KNeighbours(EdgeModel):
    pass

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter
        pb.add_number("k_neighbours", "K Neighbours", "Number of nearest neighbours", 1, 100, 1, 1, True)
        pb.add_selection("weights", "Weights", "Determines how the weights are calculated", ["uniform", "distance"], "distance", False, True)
        pb.add_selection("p", "P-Value", "", [1, 2], 1, False, True)
        return pb.parameters

    @staticmethod
    def get_name():
        return "K-Nearest Neighbours Classifier"

    @staticmethod
    def get_description():
        return "A simple K-Nearest Neighbours classifier."

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
