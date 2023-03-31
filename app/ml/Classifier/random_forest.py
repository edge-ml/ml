from app.codegen.export_javascript import export_javascript
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.models.edge_model import EdgeModel
from sklearn.ensemble import RandomForestClassifier
from app.ml.Classifier.BaseClassififer import BaseClassififer
from micromlgen import port
import m2cgen as m2c
from app.ml.Classifier.utils import reshapeSklearn
from bson.objectid import ObjectId
from app.internal.config import CLASSIFIER_STORE
import pickle
import os

import copy


class RandomForest(BaseClassififer):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.data_id = None

    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()

        pb.add_number(
            "n_estimators",
            "N-Estimators",
            "The number of trees in the forest",
            1,
            2000,
            100,
            1,
            True,
        )

        pb.add_selection(
            "criterion",
            "Criterion",
            "The function to measure the quality of a split. Supported criteria are “gini” for the Gini impurity and “entropy” for the information gain. Note: this parameter is tree-specific.",
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

        pb.add_boolean(
            "bootstrap",
            "Bootstrap Sampling",
            "Whether bootstrap samples are used when building trees. If False, the whole dataset is used to build each tree.",
            True,
            True,
        )

        pb.add_boolean(
            "oob_score",
            "OOB Score",
            "Whether to use out-of-bag samples to estimate the generalization score. Only available if bootstrap is set to True",
            False,
            True,
        )

        # user should not be able to set this
        # pb.add_number(
        #     "n_jobs",
        #     "N Jobs",
        #     "The number of jobs to run in parallel. fit, predict, decision_path and apply are all parallelized over the trees. None means 1 unless in a joblib.parallel_backend context. -1 means using all processors.",
        #     -1,
        #     10000,
        #     None,
        #     1,
        #     True,
        #     False,
        # )

        pb.add_number(
            "random_state",
            "Random State",
            "Controls both the randomness of the bootstrapping of the samples used when building trees (if bootstrap=True) and the sampling of the features to consider when looking for the best split at each node (if max_features < n_features).",
            0,
            2 ** 32 - 1,
            None,
            1,
            True,
            False,
        )

        # pb.add_number('verbose', 'Verbosity Level', 'Controls the verbosity when fitting and predicting.', 0, 1000000, 0, 1, True, False)

        pb.add_boolean(
            "warm_start",
            "Warm Start",
            "When set to True, reuse the solution of the previous call to fit and add more estimators to the ensemble, otherwise, just fit a whole new forest.",
            False,
            True,
        )

        # TODO not properly implemented
        pb.add_selection(
            "class_weight",
            "Class Weight",
            "Weights associated with classes in the form {class_label: weight}. If not given, all classes are supposed to have weight one. For multi-output problems, a list of dicts can be provided in the same order as the columns of y.",
            ["balanced", "balanced_subsample"],
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

        # TODO not properly implemented, different max values by ints and floats
        pb.add_number(
            "max_samples",
            "Max Samples",
            "If bootstrap is True, the number of samples to draw from X to train each base estimator. If None (default), then draw X.shape[0] samples. If int, then draw max_samples samples. If float, then draw max_samples * X.shape[0] samples. Thus, max_samples should be in the interval (0.0, 1.0]",
            0,
            1000000,
            None,
            0.01,
            True,
            False,
        )

        print(pb.parameters)

        return pb.parameters

    @staticmethod
    def get_name():
        return "Random Forest Classifier"

    @staticmethod
    def get_description():
        return "A simple random forest classifier."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

    def export(self, platform: InferenceFormats, window_size, labels, timeseries, scaler):
        if platform == InferenceFormats.PYTHON:
            return m2c.export_to_python(self.clf)
        elif platform == InferenceFormats.C_EMBEDDED:
            return port(self.clf)
        # elif platform == InferenceFormats.C:
        #     return m2c.export_to_c(self.clf)
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
        self.clf = RandomForestClassifier()

    def fit(self, X_train, y_train):
        X_train_reshaped = reshapeSklearn(X_train)
        self.clf.fit(X_train_reshaped, y_train)

    def predict(self, X_test):
        X_train_reshaped = reshapeSklearn(X_test)
        return self.clf.predict(X_train_reshaped)

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
    
    # @staticmethod
    # def config():
    #     return {
    #     "name": RandomForest.get_name(),
    #     "description": RandomForest.get_description(),
    #     "parameters": RandomForest.get_hyperparameters(),
    #     "platforms": RandomForest.get_platforms()
    #     }

    def get_state(self):
        return {"data_id": self.data_id}

    def restore(self, dict):
        self.data_id = dict.state["data_id"]
    
    def persisit(self):
        self.data_id = ObjectId()
        path = f'{CLASSIFIER_STORE}/{self.data_id}'
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        with open(path + "/clf.pkl", 'wb') as f:
            pickle.dump(self.clf, f)  
        return super().persist()