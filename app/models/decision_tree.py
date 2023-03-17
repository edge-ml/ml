from app.codegen.export_javascript import export_javascript
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.models.edge_model import EdgeModel
from sklearn.tree import DecisionTreeClassifier
from micromlgen import port
import m2cgen as m2c
from app.mcuConverter.mcuConverter import McuLanguage, convertMCU
from sklearn.tree import DecisionTreeClassifier

import copy

class DecisionTree(EdgeModel):

    id = 1


    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter

        pb.add_selection(
            "criterion",
            "Criterion",
            "The function to measure the quality of a split. Supported criteria are “gini” for the Gini impurity and “entropy” for the information gain.",
            ["gini", "entropy"],
            "gini",
            False,
            True,
        )

        pb.add_number(
            "max_depth",
            "Max Depth",
            "The maximum depth of the tree. If None, then nodes are expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.",
            1,
            10000,
            None,
            1,
            False,
            False,
        )

        pb.add_selection(
            "splitter",
            "Splitter",
            "The strategy used to choose the split at each node. Supported strategies are “best” to choose the best split and “random” to choose the best random split.",
            ["best", "random"],
            "best",
            False,
            True,
        )

        pb.add_number(
            "min_samples_split",
            "Min Samples Split",
            "The minimum number of samples required to split an internal node: If int, then consider min_samples_split as the minimum number. If float, then min_samples_split is a fraction and ceil(min_samples_split * n_samples) are the minimum number of samples for each split.",
            2,
            20,
            2,
            0.1,
            True,
        )

        pb.add_number(
            "min_samples_leaf",
            "Min Samples Leaf",
            "The minimum number of samples required to be at a leaf node. A split point at any depth will only be considered if it leaves at least min_samples_leaf training samples in each of the left and right branches. This may have the effect of smoothing the model, especially in regression. If int, then consider min_samples_leaf as the minimum number. If float, then min_samples_leaf is a fraction and ceil(min_samples_leaf * n_samples) are the minimum number of samples for each node.",
            1,
            20,
            1,
            0.1,
            True,
            False,
        )

        pb.add_number(
            "min_weight_fraction_leaf",
            "Min Weight Fraction Leaf",
            "The minimum weighted fraction of the sum total of weights (of all the input samples) required to be at a leaf node. Samples have equal weight when sample_weight is not provided.",
            0.0,
            10000.0,
            0.0,
            0.01,
            True,
            False,
        )

        # TODO selection with various types, how to handle: valid parameters: 'auto', 'sqrt', 'log2' or an int or float value?
        pb.add_selection(
            "max_features",
            "Max Features",
            "The number of features to consider when looking for the best split: \n If int, then consider max_features features at each split.\n If float, then max_features is a fraction and round(max_features * n_features) features are considered at each split.\n If “auto”, then max_features=sqrt(n_features).\n If “sqrt”, then max_features=sqrt(n_features) (same as “auto”).\n If “log2”, then max_features=log2(n_features).\n If None, then max_features=n_features\n Note: the search for a split does not stop until at least one valid partition of the node samples is found, even if it requires to effectively inspect more than max_features features.",
            ["auto", "sqrt", "log2"],
            "auto",
            False,
            True,
        )

        pb.add_number(
            "random_state",
            "Random State",
            "Controls the randomness of the estimator. The features are always randomly permuted at each split, even if splitter is set to \"best\". When max_features < n_features, the algorithm will select max_features at random at each split before finding the best split among them. But the best found split may vary across different runs, even if max_features=n_features. That is the case, if the improvement of the criterion is identical for several splits and one split has to be selected at random. To obtain a deterministic behaviour during fitting, random_state has to be fixed to an integer.",
            0,
            2 ** 32 - 1,
            None,
            1,
            True,
            False,
        )

        pb.add_number(
            "max_leaf_nodes",
            "Max Leaf Nodes",
            "Grow trees with max_leaf_nodes in best-first fashion. Best nodes are defined as relative reduction in impurity. If None then unlimited number of leaf nodes.",
            2,
            100000,
            None,
            1,
            True,
            False,
        )

        pb.add_number(
            "min_impurity_decrease",
            "Min Impurity Decrease",
            "A node will be split if this split induces a decrease of the impurity greater than or equal to this value. The weighted impurity decrease equation is the following: N_t / N * (impurity - N_t_R / N_t * right_impurity - N_t_L / N_t * left_impurity) where N is the total number of samples, N_t is the number of samples at the current node, N_t_L is the number of samples in the left child, and N_t_R is the number of samples in the right child. N, N_t, N_t_R and N_t_L all refer to the weighted sum, if sample_weight is passed.",
            0.0,
            100.0,
            0.0,
            0.01,
            True,
            False,
        )

        # TODO missing dict / list of dicts parameter
        pb.add_selection(
            "class_weight",
            "Class Weight",
            "Weights associated with classes in the form {class_label: weight}. If None, all classes are supposed to have weight one. The “balanced” mode uses the values of y to automatically adjust weights inversely proportional to class frequencies in the input data as n_samples / (n_classes * np.bincount(y))",
            ["balanced"],
            None,
            False,
            True,
        )

        pb.add_number(
            "ccp_alpha",
            "CCP Alpha",
            "Complexity parameter used for Minimal Cost-Complexity Pruning. The subtree with the largest cost complexity that is smaller than ccp_alpha will be chosen. By default, no pruning is performed.",
            0.0,
            10000.0,
            0.0,
            0.01,
            True,
            False,
        )

        return pb.parameters

    @staticmethod
    def get_name():
        return "Decision Tree Classifier"

    @staticmethod
    def get_description():
        return "A simple decision tree classifier."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

    def export(self, platform: InferenceFormats, window_size, labels, timeseries, scaler):
        if platform == InferenceFormats.PYTHON:
            return m2c.export_to_python(self.clf)
        elif platform == InferenceFormats.C_EMBEDDED:
        #     return port(self.clf)
        # elif platform == InferenceFormats.C:
            return m2c.export_to_c(self.clf)
        elif platform == InferenceFormats.JAVASCRIPT:
            return export_javascript(self)
        elif platform == InferenceFormats.CPP:
            return convertMCU(self, window_size, labels, timeseries, scaler, language=McuLanguage.CPP)
        elif platform == InferenceFormats.C:
            return convertMCU(self, window_size, labels, timeseries, scaler, language=McuLanguage.C)
        else:
            print(platform)
            raise NotImplementedError

    # class methods
    def __init__(self, hyperparameters={}):
        super().__init__(hyperparameters)
        self.clf = DecisionTreeClassifier()

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error

    @staticmethod
    def config():
        return {
        "name": DecisionTree.get_name(),
        "description": DecisionTree.get_description(),
        "id": DecisionTree.id,
        "hyperparameters": DecisionTree.get_hyperparameters(),
        "platforms": DecisionTree.get_platforms()
        }