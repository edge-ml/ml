from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
from app.ml.Pipelines.Categories.Classifier.random_forest import RandomForest
from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
from app.ml.Pipelines.Categories.Classifier.KMeansClassifier import KMeansClassifier

from app.ml.Pipelines.Abstract.AbstractPipelineCategory import PipelineCategory

from typing import List

CLASSIFIERS : List[BaseClassififer] = [DecisionTree, RandomForest]

def get_classifier_by_name(name):
    for cls in CLASSIFIERS:
        if cls.get_name() == name:
            return cls
    raise Exception()

CLASSIFIER_CONFIG = [x.get_train_config() for x in CLASSIFIERS]

CLASSIFIER_CATEGORY = PipelineCategory("Classifier", "Classification for time-series data", CLASSIFIER_CONFIG)
    