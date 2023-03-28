from app.ml.Evaluation.BaseEvaluation import BaseEvaluation
from app.utils.parameter_builder import ParameterBuilder
from sklearn.model_selection import train_test_split
from app.ml.Evaluation.utils import calculateMetrics
from app.ml.Normalizer.BaseNormalizer import BaseNormalizer
import numpy as np

from app.ml.Classifier import Classifier

class TestTrainSplitEvaluation(BaseEvaluation):
    def __init__(self, train_x, train_y, classifier: Classifier, classifier_parameters, normalizer: BaseNormalizer, normalizer_parameters, labels, parameters):
        super().__init__(train_x, train_y, classifier, classifier_parameters, normalizer, normalizer_parameters, labels, parameters)
        self.clf = classifier(classifier_parameters)
        self.norm = normalizer(normalizer_parameters)

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

    def train_eval(self):
        part = int(self.get_param_value_by_name("Train_test_split") / 100 * len(self.train_x))
        p = np.random.permutation(len(self.train_x))
        random_train_x = self.train_x[p]
        random_train_y = self.train_y[p]

        train_x = random_train_x[:part]
        train_y = random_train_y[:part]
        test_x = random_train_x[part:]
        test_y = random_train_y[part:]
        train_x = self.norm.fit_normalize(train_x)
        test_x = self.norm.normalize(test_x)

        self.clf.fit(train_x, train_y)

        metrics = calculateMetrics(test_y, self.clf.predict(test_x), self.labels)
        self.metrics = metrics


    def persist(self):
        normalizer_state = self.norm.persist()
        classifier_state = self.clf.persist()
        evaluation_state = {"name": self.get_name(), "parameters": self.parameters}
        return {"normalizer": normalizer_state, "classifier": classifier_state, "evaluation": evaluation_state, "metrics": self.metrics}