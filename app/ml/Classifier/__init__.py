from app.ml.Classifier.Classifier import Classifier
from app.ml.Classifier.decision_tree import DecisionTree
from app.ml.Classifier.random_forest import RandomForest

CLASSIFIERS = [DecisionTree]

def get_classifier_by_name(name):
    for cls in CLASSIFIERS:
        if cls.get_name() == name:
            return cls
    raise Exception()

CLASSIFIER_CONFIG = [x.config() for x in CLASSIFIERS]