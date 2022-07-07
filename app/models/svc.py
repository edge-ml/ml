from app.codegen.export_javascript import export_javascript
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.models.edge_model import EdgeModel
from sklearn.svm import SVC as SVCHoist
from micromlgen import port
import m2cgen as m2c
from app.mcuConverter.mcuConverter import convertMCU

import copy

class SVC(EdgeModel):
    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter

        pb.add_number(
            "C",
            "C",
            "Regularization parameter. The strength of the regularization is inversely proportional to C. Must be strictly positive. The penalty is a squared l2 penalty.",
            0.01,
            100000.0,
            1.0,
            0.01,
            True,
            False,
        )

        pb.add_selection(
            "kernel",
            "Kernel",
            "Specifies the kernel type to be used in the algorithm.",
            ["linear", "poly", "rbf", "sigmoid", "precomputed"],
            "rbf",
            False,
            True,
        )

        pb.add_number(
            "degree",
            "Degree",
            "Degree of the polynomial kernel function (‘poly’). Ignored by all other kernels.",
            1,
            100000,
            3,
            1,
            True,
            False,
        )

        # TODO not implemented fully, also supports passing float as a fixed gamma
        pb.add_selection(
            "gamma",
            "Gamma",
            "Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’.\nif gamma='scale' (default) is passed then it uses 1 / (n_features * X.var()) as value of gamma,\nif ‘auto’, uses 1 / n_features.",
            ["scale", "auto"],
            "scale",
            False,
            True,
        )

        pb.add_number(
            "coef0",
            "coef0",
            "Independent term in kernel function. It is only significant in ‘poly’ and ‘sigmoid’.",
            0.0,
            100000.0,
            0.0,
            0.01,
            True,
        )

        pb.add_boolean(
            "shrinking",
            "Shrinking",
            "Whether to use the shrinking heuristic.",
            True,
            True,
        )

        pb.add_boolean(
            "probability",
            "Probability",
            "Whether to enable probability estimates.",
            False,
            True,
        )

        pb.add_number(
            "tol",
            "Tolerance",
            "Tolerance for stopping criterion.",
            0.000001,
            100000.0,
            0.001,
            0.000001,
            True,
            False,
        )

        pb.add_number(
            "cache_size",
            "Cache Size",
            "Specify the size of the kernel cache (in MB).",
            0.0,
            1000.0,
            200.0,
            0.01,
            True,
            False,
        )

        # TODO Not implemented correctly, missing dict / list of dicts parameter
        pb.add_selection(
            "class_weight",
            "Class Weight",
            "Set the parameter C of class i to class_weight[i]*C for SVC. If not given, all classes are supposed to have weight one. The “balanced” mode uses the values of y to automatically adjust weights inversely proportional to class frequencies in the input data as n_samples / (n_classes * np.bincount(y)).",
            ["balanced"],
            None,
            False,
            True,
        )

        # skipping verbose

        pb.add_number(
            "max_iter",
            "Max Iterations",
            "Hard limit on iterations within solver, or -1 for no limit.",
            -1,
            100000,
            -1,
            1,
            True,
            False,
        )

        pb.add_selection(
            "decision_function_shape",
            "Decision Function Shape",
            "Whether to return a one-vs-rest (‘ovr’) decision function of shape (n_samples, n_classes) as all other classifiers, or the original one-vs-one (‘ovo’) decision function of libsvm which has shape (n_samples, n_classes * (n_classes - 1) / 2). However, one-vs-one (‘ovo’) is always used as multi-class strategy. The parameter is ignored for binary classification.",
            ["ovo", "ovr"],
            "ovr",
            False,
            True,
        )

        pb.add_boolean(
            "break_ties",
            "Break Ties",
            "If true, decision_function_shape='ovr', and number of classes > 2, predict will break ties according to the confidence values of decision_function; otherwise the first class among the tied classes is returned. Please note that breaking ties comes at a relatively high computational cost compared to a simple predict.",
            False,
            True,
        )

        pb.add_number(
            "random_state",
            "Random State",
            "Controls the pseudo random number generation for shuffling the data for probability estimates. Ignored when probability is False. Pass an int for reproducible output across multiple function calls.",
            0,
            2 ** 32 - 1,
            None,
            1,
            True,
            False,
        )

        return pb.parameters

    @staticmethod
    def get_name():
        return "SVC Classifier"

    @staticmethod
    def get_description():
        return "A simple SVC classifier."

    @staticmethod
    def get_platforms():
        # return [InferenceFormats.PYTHON, InferenceFormats.C, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP]
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT]

    def export(self, platform: InferenceFormats, window_size, labels, timeseries, scaler):
        if platform == InferenceFormats.PYTHON:
            return m2c.export_to_python(self.clf)
        # FIXME: gives error: You probably didn't set an explicit value for gamma: 0.001 is a good default
        # but sklearn defaults to 'scale'
        # elif platform == InferenceFormats.C_EMBEDDED:
        #     return port(self.clf)
        elif platform == InferenceFormats.C:
            return m2c.export_to_c(self.clf)
        elif platform == InferenceFormats.JAVASCRIPT:
            return export_javascript(self)
        # FIXME: This suffers from the same error as above
        # elif platform == InferenceFormats.CPP:
        #     return convertMCU(self, window_size, labels, timeseries)
        else:
            print(platform)
            raise NotImplementedError

    # class methods
    def __init__(self, hyperparameters={}):
        super().__init__(hyperparameters)
        self.clf = SVCHoist()

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error

