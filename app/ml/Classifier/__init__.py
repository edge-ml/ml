from app.ml.Classifier.BaseClassififer import BaseClassififer
from app.ml.Classifier.decision_tree import DecisionTree
from app.ml.Classifier.NeuralNetwork import NeuralNetwork
from app.ml.Classifier.DenseSmall import DenseSmall
from app.ml.Classifier.DenseMedium import DenseMedium
from app.ml.Classifier.DenseLarge import DenseLarge
from app.ml.Classifier.CNNSmall import CNNSmall
from app.ml.Classifier.random_forest import RandomForest
from app.ml.Classifier.BaseClassififer import BaseClassififer
from typing import List

CLASSIFIERS : List[BaseClassififer] = [DecisionTree, DenseSmall, DenseMedium, DenseLarge, CNNSmall]

def get_classifier_by_name(name):
    for cls in CLASSIFIERS:
        if cls.get_name() == name:
            return cls
    raise Exception()

CLASSIFIER_CONFIG = [x.get_train_config() for x in CLASSIFIERS]