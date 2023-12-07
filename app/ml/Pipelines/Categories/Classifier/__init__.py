from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
from app.ml.Pipelines.Categories.Classifier.random_forest import RandomForest
from app.ml.Pipelines.Categories.Classifier.NeuralNetwork import NeuralNetwork
from app.ml.Pipelines.Categories.Classifier.DenseSmall import DenseSmall
from app.ml.Pipelines.Categories.Classifier.CNNSmall import CNNSmall
from app.ml.Pipelines.Categories.Classifier.DenseMedium import DenseMedium
from app.ml.Pipelines.Categories.Classifier.DenseLarge import DenseLarge
from app.ml.Pipelines.Categories.Classifier.CNNSmall import CNNSmall

from app.ml.Pipelines.Categories.Classifier.KMeansClassifier import KMeansClassifier

from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep

from typing import List

CLASSIFIERS : List[BaseClassififer] = [DecisionTree, RandomForest, DenseSmall, DenseMedium, DenseLarge, CNNSmall]

def get_classifier_by_name(name):
    for cls in CLASSIFIERS:
        if cls.get_name() == name:
            return cls
    raise Exception()

CLASSIFIER_CATEGORY = AbstractPipelineStep("Classifier", "Classification for time-series data", CLASSIFIERS)
    