from typing import List
import os
import importlib
import inspect
import fnmatch

from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator
from app.ml.Pipelines.AutoMLClassificationPipeline import AutoMLClassificationPipeline
from app.ml.Pipelines.ManualClassificationPipeline import ManualClassificationPipeline

_pipelines : List[AbstractPipeLineCreator] = [ManualClassificationPipeline, AutoMLClassificationPipeline]


def get_configs():
    return [x.get_train_config() for x in _pipelines]

PIPELINES_CONFIG = get_configs()


from app.ml.Pipelines.Categories.Windowing.SampleWindower import SampleWindower
from app.ml.Pipelines.AutoML.AutoMLClassifier import AutoMLClassifier
from app.ml.Pipelines.Categories.Common.ModelMetadata import ModelMetadata
from app.ml.Pipelines.Categories.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor
from app.ml.Pipelines.Categories.Classifier.decision_tree import DecisionTree
from app.ml.Pipelines.Categories.Classifier.DenseSmall import DenseSmall
from app.ml.Pipelines.Categories.Classifier.CNNSmall import CNNSmall
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer


PipelineSteps = [SampleWindower, AutoMLClassifier, ModelMetadata, TestTrainSplitEvaluation, SimpleFeatureExtractor, DecisionTree, MinMaxNormalizer, ZNormalizer, DenseSmall, NoFeatureExtractor, CNNSmall]

_pipelineMap = {x.get_name(): x for x in PipelineSteps}


def getProcessor(name):
    return _pipelineMap[name]


from app.ml.Pipelines.Categories.Windowing import WINDOWING_CATEGORY
from app.ml.Pipelines.AutoML import AUTOMLCLASSIFIER_CATEGORY
from app.ml.Pipelines.Categories.Common import COMMON_CATEGORY
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CATEGORY
from app.ml.Pipelines.Categories.FeatureExtraction import FEATUREEXTRACTION_CATEGORY
from app.ml.Pipelines.Categories.Normalizer import NORMALIZER_CATEGORY
from app.ml.Pipelines.Categories.Classifier import CLASSIFIER_CATEGORY


Categories = [WINDOWING_CATEGORY, AUTOMLCLASSIFIER_CATEGORY, COMMON_CATEGORY, EVALUATION_CATEGORY, FEATUREEXTRACTION_CATEGORY, NORMALIZER_CATEGORY, CLASSIFIER_CATEGORY]

_categoryMap = {x.name : x for x in Categories}

def getCategory(name):
    return _categoryMap[name]
