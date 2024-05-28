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


# _pipelines : List[AbstractPipeLineCreator] = [ManualClassificationPipeline, AutoMLClassificationPipeline]
_pipelines : List[AbstractPipeLineCreator] = [ManualClassificationPipeline]


def get_configs():
    return [x.get_train_config() for x in _pipelines]

PIPELINES_CONFIG = get_configs()



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


def load_modules(dictionary, superClass):
    classes = []
    for root, _, files in os.walk(dictionary):
        for file in files:
            if file.endswith(".py"):
                if superClass.__name__ in file:
                    continue
                if file.startswith("__init__"):
                    continue
                module_path = os.path.join(root, file)
                module_path = module_path.replace(os.path.sep, ".")[2:-3]
                module = importlib.import_module(module_path)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, superClass):
                        classes.append(obj)
    return classes

_pipelineOptions = load_modules("./app/ml/Pipelines/", AbstractPipelineOption)

_pipelineMap = {}
PIPELINEOPTIONCONFIGS = []
for x in _pipelineOptions:
    try:
        name = x.get_name()
        _pipelineMap[name] = x
        PIPELINEOPTIONCONFIGS.append(x.get_train_config())
    except Exception as e:
        pass

def getPipelineOption(name):
    return _pipelineMap[name]

def getPipeline(model):
    stepOptions = model.pipeline.selectedPipeline.steps
    categories = [getCategory(x.name) for x in stepOptions]
    options = [getPipelineOption(x.options.name)() for x in stepOptions]
    for o, s in zip(options, stepOptions):
        print("RESTORE_DATA: ", s.options.input_shape, s.options.output_shape)
        o.restore(s.options)
    pipeline = Pipeline(options=options, steps=categories)  
    return pipeline