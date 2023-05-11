from app.ml.Evaluation.BaseEvaluation import BaseEvaluation
from app.utils.parameter_builder import ParameterBuilder
from sklearn.model_selection import train_test_split
from app.ml.Evaluation.utils import calculateMetrics
from app.DataModels.PipeLine import PipeLineStep
from typing import Optional, Tuple
import numpy as np

from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Classifier import get_classifier_by_name


class KFold(BaseEvaluation):

    def __init__(self, normalizer_config: PipeLineStep, classifier_config: PipeLineStep, evaluation_config: PipeLineStep):
        super().__init__(normalizer_config, classifier_config, evaluation_config)

    @staticmethod
    def get_name():
        return "KFold"

    @staticmethod
    def get_description():
        return "Evaluates a model by splitting the dataset into k consecutive folds."

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number("n_splits", "folds", "Number of folds", 2, 999999, 5, 1, required=True)
        return pb.parameters

    def eval(self, X, Y, labels) -> Tuple[dict, Tuple[None, None]]:
        print("KFolding")
        n_splits = int(self.get_param_value_by_name("n_splits"))

        if n_splits <= 1:
            raise ValueError("n_splits must be greater than 1")
        if len(X) != len(Y):
            raise ValueError("X and y must have the same number of samples")
        if n_splits > len(X):
            raise ValueError("n_splits cannot be greater than the number of samples")
        
        n_samples = len(X)
        folds = np.array_split(np.random.permutation(n_samples), n_splits)
        Y_pred = np.empty_like(Y)

        for i in range(n_splits):
            print('fold ', i)
            test_idx = folds[i]
            train_idx = np.hstack(folds[:i] + folds[i+1:])
            X_train, Y_train = X[train_idx], Y[train_idx]
            X_test, Y_test = X[test_idx], Y[test_idx]

            normalizer = get_normalizer_by_name(self.normalizer_config.name)(self.normalizer_config.parameters)
            X_train_norm = normalizer.fit_normalize(X_train)
            X_test_norm = normalizer.normalize(X_test)

            classifier = get_classifier_by_name(self.classifier_config.name)(self.classifier_config.parameters)
            classifier.fit(X_train_norm, Y_train)

            Y_pred[test_idx] = classifier.predict(X_test_norm)
        
        self.metrics = calculateMetrics(Y, Y_pred, labels)
        return self.metrics, (None, None)

    def persist(self):
        return {"name": self.get_name(), "parameters": self.parameters, "metrics": self.metrics}