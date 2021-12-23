from utils.parameter_builder import ParameterBuilder
from models.edge_model import EdgeModel
import copy


class MLP(EdgeModel):
    pass

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter
        pb.add_number("c_value", "C Value", "", 0.03125, 32768., 1.0, 0.00001, True, True)
        pb.add_selection("kernel", "Kernel", "", ["rbf", "poly", "sigmoid"], "rbf", False, True)
        pb.add_number("degree", "Degree", "", 2, 5, 3, 1, True)
        pb.add_number("gamma", "Gamma", "", 3.0517578125e-05, 8., 0.1, 0.1, True)
        pb.add_number("coef0", "Coef0", "", -1, 1, 0, 0.1, True)
        pb.add_boolean("shrinking", "Shrinking Heuristic", "Shrinking desc", True, True)
        pb.add_number("tol", "Tol", "", 1e-5, 1e-1, 1e-3, 1e-5, True, True)
        # pb.add_number("max_iter")
        # TODO conditions
        # degree_depends_on_poly = EqualsCondition(degree, kernel, "poly")
        # coef0_condition = InCondition(coef0, kernel, ["poly", "sigmoid"])


        return pb.parameters

    @staticmethod
    def get_name():
        return "MLP Classifier"

    @staticmethod
    def get_description():
        return "A simple MLP classifier."

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
