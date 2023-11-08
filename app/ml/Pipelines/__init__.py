from typing import List
import os
import importlib
import inspect
import fnmatch

from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator
from app.ml.Pipelines.AutoMLClassificationPipeline import AutoMLClassificationPipeline
from app.ml.Pipelines.ManualClassificationPipeline import ManualClassificationPipeline
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.Pipeline import Pipeline


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


# PipelineSteps = [SampleWindower, AutoMLClassifier, ModelMetadata, TestTrainSplitEvaluation, SimpleFeatureExtractor, DecisionTree, MinMaxNormalizer, ZNormalizer, DenseSmall, NoFeatureExtractor, CNNSmall]

# _pipelineMap = {x.get_name(): x for x in PipelineSteps}


# def getProcessor(name):
#     return _pipelineMap[name]


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


def load_modules():
    print("LOAD MODULES")
    classes = []
    dic = "./app/ml/Pipelines/"
    for root, _, files in os.walk(dic):
        for file in files:
            if file.endswith(".py"):
                if "AbstractPipelineOption" in file:
                    continue
                if file.startswith("__init__"):
                    continue
                module_path = os.path.join(root, file)
                module_path = module_path.replace(os.path.sep, ".")[2:-3]
                module = importlib.import_module(module_path)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, AbstractPipelineOption):
                        classes.append(obj)
    return classes

_classes = load_modules()

_pipelineMap = {}
for x in _classes:
    try:
        name = x.get_name()
        _pipelineMap[name] = x
    except Exception as e:
        pass


def getProcessor(name):
    return _pipelineMap[name]

def getPipeline(model):
    stepOptions = model.pipeline.selectedPipeline.steps
    options = [getProcessor(x.options.name)() for x in stepOptions]
    for o, s in zip(options, stepOptions):
        o.restore(s.options)
    pipeline = Pipeline(options=options, steps=[])  
    return pipeline