from app.ml.Classifier import Classifier
from app.ml.Normalizer.BaseNormalizer import BaseNormalizer

class EvaluationStrategy():

    def __init__(self, train_x, train_y, classifier: Classifier, normalizer: BaseNormalizer, labels, parameters):
        self.train_x = train_x
        self.train_y = train_y
        self.classifier = classifier
        self.normalizer = normalizer
        self.labels = labels
        self.parameters = parameters

    def getParameter(self, name):
        for param in self.parameters:
            if (param["name"] == name):
                return param
 
    def train_eval(self):
        raise NotImplementedError
    
    @staticmethod
    def config(self):
        raise NotImplementedError()

    def persist():
        raise NotImplementedError()