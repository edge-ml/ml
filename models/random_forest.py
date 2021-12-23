from utils.parameter_builder import ParameterBuilder
from models.edge_model import EdgeModel
import copy


class RandomForest(EdgeModel):
    pass

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter
        pb.add_selection(
            "criterion", "Criterion", "", ["gini", "entropy"], "entropy", False, True
        )
        pb.add_number("max_features", "Max Features", "", 0.0, 1.0, 0.5, 0.01, True)
        # pb.add_number("max_depth", )
        pb.add_number("min_samples_split", "Min Samples Split", "", 2, 20, 2, 1, True)
        pb.add_number("min_samples_leaf", "Min Samples Leaf", "", 1, 20, 1, True)
        # pb.add_number("min_weight_fraction_leaf")
        # pb.add_number("max_leaf_nodes")
        # pb.add_number("min_impurity_decrease")
        pb.add_boolean(
            "bootstrap",
            "Bootstrap Sampling",
            "Bootstrap Sampling is a method that involves drawing of sample data repeatedly with replacement from a data source to estimate a population parameter.",
            True,
            True,
        )
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
        labels = ["a", "b"]
        confusion_matrix = [[5, 0], [0, 5]]
        return (labels, confusion_matrix)

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
