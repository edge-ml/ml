from app.ml.Classifier import Classifier
from app.ml.Normalizer.Normalizer import Normalizer

class EvaluationStrategy():

    def __init__(self, train_x, train_y, classifier: Classifier, normalizer: Normalizer, parameters):
        self.train_x = train_x
        self.train_y = train_y
        self.classifier = classifier
        self.normalizer = normalizer
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