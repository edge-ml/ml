from app.ml.Evaluation.BaseEvaluation import BaseEvaluation
from app.ml.Windowing.BaseWindower import BaseWindower
from app.utils.parameter_builder import ParameterBuilder
from sklearn.model_selection import train_test_split
from app.ml.Evaluation.utils import calculateMetrics
from app.ml.Normalizer.BaseNormalizer import BaseNormalizer
from app.DataModels.PipeLine import PipeLineStep
from typing import List
import numpy as np

from app.ml.Windowing import get_windower_by_name
from app.ml.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Classifier import get_classifier_by_name

from app.ml.Pipeline import Pipeline


from app.ml.Classifier import BaseClassififer

class TestTrainSplitEvaluation(BaseEvaluation):

    def __init__(self, windower_config: PipeLineStep, featureExtractor_config: PipeLineStep, normalizer_config: PipeLineStep, classifier_config: PipeLineStep, datasets: np.ndarray, labels: List[str], evaluation_config: PipeLineStep):
        super().__init__(windower_config, featureExtractor_config, normalizer_config, classifier_config, datasets, labels, evaluation_config)
        
        self.windower : BaseWindower = get_windower_by_name(windower_config.name)(windower_config.parameters)
        self.classifier = get_classifier_by_name(classifier_config.name)(classifier_config.parameters)
        self.normalizer = get_normalizer_by_name(normalizer_config.name)(windower_config.parameters)
        self.windower = get_windower_by_name(windower_config.name)(windower_config.parameters)
        self.featureExtractor = get_feature_extractor_by_name(featureExtractor_config.name)(featureExtractor_config.parameters)

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

    def train_eval(self) -> Pipeline:

        train_X, train_Y = self.windower.window(self.datasets)
        train_x, train_Y = self.featureExtractor.extract_features(train_X, train_Y)


        part = int(self.get_param_value_by_name("Train_test_split") / 100 * len(train_X))
        p = np.random.permutation(len(train_X))
        random_train_x = train_X[p]
        random_train_y = train_Y[p]

        train_x = random_train_x[:part]
        train_y = random_train_y[:part]
        test_x = random_train_x[part:]
        test_y = random_train_y[part:]
        train_x = self.normalizer.fit_normalize(train_x)
        test_x = self.normalizer.normalize(test_x)

        self.classifier.fit(train_x, train_y)

        self.metrics = calculateMetrics(test_y, self.classifier.predict(test_x), self.labels)
        return Pipeline(self.windower, self.featureExtractor, self.normalizer, self.classifier)

    def persist(self):
        steps = {"windower": self.windower.persist(), "featureExtractor": self.featureExtractor.persist(), "normalizer": self.normalizer.persist(), "classifier": self.classifier.persist()}
        evaluation_state = {"name": self.get_name(), "parameters": self.parameters, "steps": steps, "metrics": self.metrics}
        return evaluation_state