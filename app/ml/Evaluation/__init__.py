from app.ml.Evaluation.BaseEvaluation import BaseEvaluation
from app.ml.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation
from typing import List

EVALAUTIONS : List[BaseEvaluation] = [
    TestTrainSplitEvaluation
]

def getConfig():
    return [{"name": x.name(), "parameters": x.config()} for x in EVALAUTIONS]

def get_eval_by_name(name):
    for evl in EVALAUTIONS:
        if evl.get_name() == name:
            return evl
    raise KeyError(f"Evlaluation {name} not found")
    
EVALUATION_CONFIG = [x.get_train_config() for x in EVALAUTIONS]