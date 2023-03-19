from app.ml.Evaluation import EvaluationStrategy
from app.ml.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation

EVALAUTIONS = [
    TestTrainSplitEvaluation
]

eval_map = {x.name(): x for x in EVALAUTIONS}

def getConfig():
    return [{"name": x.name(), "parameters": x.config()} for x in EVALAUTIONS]

def get_eval_by_name(name):
    if name in eval_map:
        return eval_map[name]
    else:
        raise Exception()
    
EVALUATION_CONFIG = [x.config() for x in EVALAUTIONS]