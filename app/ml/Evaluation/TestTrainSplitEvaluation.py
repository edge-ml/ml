from app.ml.Evaluation.EvaluationStrategy import EvaluationStrategy
from app.utils.parameter_builder import ParameterBuilder
from sklearn.model_selection import train_test_split
from app.ml.Evaluation.utils import calculateMetrics
from app.ml.Normalizer.Normalizer import Normalizer
import numpy as np

from app.ml.Classifier import Classifier

class TestTrainSplitEvaluation(EvaluationStrategy):
    def __init__(self, train_x, train_y, classifier: Classifier, normalizer: Normalizer, labels, parameters):
        super().__init__(train_x, train_y, classifier, normalizer, labels, parameters)

    @staticmethod
    def name():
        return "TestTrainSplit"

    @staticmethod
    def config():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number("Train_test_split", "split", "Ratio between training and testing data", 0, 100, 80, 1, required=True)
        return {"name": TestTrainSplitEvaluation.name(), "parameters": pb.parameters}

    def train_eval(self):
        print(self.train_x.shape, self.train_y.shape)

        part = int(self.getParameter("Train_test_split")["value"] / 100 * len(self.train_x))
        p = np.random.permutation(len(self.train_x))
        random_train_x = self.train_x[p]
        random_train_y = self.train_y[p]

        train_x = random_train_x[:part]
        train_y = random_train_y[:part]
        test_x = random_train_x[part:]
        test_y = random_train_y[part:]
        print(train_x.shape)
        train_x = self.normalizer.fit_normalize(train_x)
        test_x = self.normalizer.normalize(test_x)

        self.classifier.fit(train_x, train_y)

        metrics = calculateMetrics(test_y, self.classifier.predict(test_x), self.labels)
        self.metrics = metrics


    def persist(self):
        normalizer_state = self.normalizer.get_state()
        print("normalizer: ")
        print(self.normalizer)
        print(normalizer_state)
        classifier_state = self.classifier.get_state()
        evaluation_state = {"name": TestTrainSplitEvaluation.name(), "parameter": self.parameters}
        return {"normalizer": normalizer_state, "classifier": classifier_state, "evaluation": evaluation_state, "metrics": self.metrics}