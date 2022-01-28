from app.utils.parameter_builder import ParameterBuilder
from app.models.edge_model import EdgeModel
from sklearn.svm import SVC
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
    def __init__(self, hyperparameters={}):
        super().__init__(hyperparameters)
        self.clf = SVC()

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
