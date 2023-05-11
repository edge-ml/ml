from app.ml.Evaluation.BaseEvaluation import BaseEvaluation
from app.utils.parameter_builder import ParameterBuilder
from sklearn.model_selection import train_test_split
from app.ml.Evaluation.utils import calculateMetrics
from app.ml.Normalizer.BaseNormalizer import BaseNormalizer
from app.DataModels.PipeLine import PipeLineStep
from typing import Tuple
import numpy as np

from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Classifier import get_classifier_by_name

from app.ml.Classifier import BaseClassififer

class TestTrainSplitEvaluation(BaseEvaluation):

    def __init__(self, normalizer_config: PipeLineStep, classifier_config: PipeLineStep, evaluation_config: PipeLineStep):
        super().__init__(normalizer_config, classifier_config, evaluation_config)

    @staticmethod
    def get_name():
        return "TestTrainSplit"

    @staticmethod
    def get_description():
        return "Evaluates a model by splitting the datast into a training / testing - set"

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number("Train_test_split", "split", "Ratio between training and testing data", 0, 100, 80, 1, required=True)
        return pb.parameters

    def eval(self, X, Y, labels) -> Tuple[dict, Tuple[BaseNormalizer, BaseClassififer]]:
        part = int(self.get_param_value_by_name("Train_test_split") / 100 * len(X))
        p = np.random.permutation(len(X))
        random_train_x = X[p]
        random_train_y = Y[p]

        train_x = random_train_x[:part]
        train_y = random_train_y[:part]
        test_x = random_train_x[part:]
        test_y = random_train_y[part:]

        normalizer = get_normalizer_by_name(self.normalizer_config.name)(self.normalizer_config.parameters)
        train_x = normalizer.fit_normalize(train_x)
        test_x = normalizer.normalize(test_x)

        classifier = get_classifier_by_name(self.classifier_config.name)(self.classifier_config.parameters)
        classifier.fit(train_x, train_y)

        self.metrics = calculateMetrics(test_y, classifier.predict(test_x), labels)
        return self.metrics, (normalizer, classifier)

    def persist(self):
        return {"name": self.get_name(), "parameters": self.parameters, "metrics": self.metrics}