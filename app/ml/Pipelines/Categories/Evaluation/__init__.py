from app.ml.Pipelines.Categories.Evaluation.BaseEvaluation import BaseEvaluation
from app.ml.Pipelines.Categories.Evaluation.KFold import KFold
from app.ml.Pipelines.Categories.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation
from app.ml.Pipelines.Abstract.AbstractPipelineStep import PipelineCategory
from typing import List

EVALAUTIONS : List[BaseEvaluation] = [
    TestTrainSplitEvaluation,
    KFold,
]

def getConfig():
    return [{"name": x.name(), "parameters": x.config()} for x in EVALAUTIONS]

def get_eval_by_name(name):
    for evl in EVALAUTIONS:
        if evl.get_name() == name:
            return evl
    raise KeyError(f"Evlaluation {name} not found")
    
EVALUATION_CONFIG = [x.get_train_config() for x in EVALAUTIONS]

EVALUATION_CATEGORY =  PipelineCategory("Evaluator", "Defines the evaluation strategy to be used.", EVALUATION_CONFIG)