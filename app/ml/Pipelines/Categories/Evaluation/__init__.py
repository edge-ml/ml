from ml.Pipelines.Categories.Evaluation.BaseEvaluation import BaseEvaluation
from ml.Pipelines.Categories.Evaluation.KFold import KFold
from ml.Pipelines.Categories.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation
from ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep, StepType
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

EVALUATION_CATEGORY =  AbstractPipelineStep("Evaluator", "Defines the evaluation strategy to be used.", EVALAUTIONS, type=StepType.EVAL)