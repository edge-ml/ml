from app.ml.Classifier import Classifier
from app.ml.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.BaseConfig import BaseConfig

class BaseEvaluation(BaseConfig):

    def __init__(self, train_x, train_y, classifier: Classifier, classifier_Config, normalizer: BaseNormalizer, normalizer_config, labels, parameters):
        super().__init__(parameters)
        self.train_x = train_x
        self.train_y = train_y
        self.classifier = classifier
        self.classifier_config = classifier_Config
        self.normalizer = normalizer
        self.normalizer_config = normalizer_config
        self.labels = labels