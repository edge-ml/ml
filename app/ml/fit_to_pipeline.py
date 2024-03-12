import numpy as np
from typing import Tuple
from DataModels.trainRequest import TrainRequest
from ml.Pipelines.Categories.Classifier import get_classifier_by_name
from ml.Pipelines.Categories.Evaluation import BaseEvaluation, get_eval_by_name
from ml.Pipelines.Categories.FeatureExtraction import get_feature_extractor_by_name
from ml.Pipelines.Categories.Normalizer import get_normalizer_by_name
from ml.Pipeline import Pipeline
from ml.Pipelines.Categories.Windowing import get_windower_by_name
from DataModels.PipelineRequest import PipelineRequest
from ml.Pipelines import getPipelineOption, getCategory
from ml.Pipelines.Abstract.AbstractPipelineStep import StepType
from ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption

def fit_to_pipeline2(trainReq : TrainRequest, datasets, labels) -> Tuple[Pipeline, BaseEvaluation]:

    windower = get_windower_by_name(trainReq.windowing.name)(trainReq.windowing.parameters)
    featureExtractor = get_feature_extractor_by_name(trainReq.featureExtractor.name)(trainReq.featureExtractor.parameters)
    evaluator = get_eval_by_name(trainReq.evaluation.name)(trainReq.normalizer, trainReq.classifier, trainReq.evaluation)
    
    X, Y = windower.window(datasets)
    X, Y = featureExtractor.extract_features(X, Y)
    metrics, (eval_normalizer, eval_classifier) = evaluator.eval(X, Y, labels)

    normalizer = eval_normalizer
    classifier = eval_classifier
    if (not normalizer) or (not classifier) or (not trainReq.useBestModelFromEvaluation): # https://stats.stackexchange.com/a/52277
        normalizer = get_normalizer_by_name(trainReq.normalizer.name)(trainReq.normalizer.parameters)
        classifier = get_classifier_by_name(trainReq.classifier.name)(trainReq.classifier.parameters)

        p = np.random.permutation(len(X))
        rX = X[p]
        rY = Y[p]

        rX = normalizer.fit_normalize(rX)
        classifier.fit(rX, rY)

    return Pipeline(windower, featureExtractor, normalizer, classifier), evaluator


def fit_to_pipeline(req: PipelineRequest, datasets, datasetMetaData, labels) -> Tuple[Pipeline, BaseEvaluation]:

    data = {"datasets": datasets, "datasetMetadata": datasetMetaData}
    pipelineSteps = []
    for step in req.selectedPipeline.steps:
        category = getCategory(step.name)
        stepProcessor = getPipelineOption(step.options.name)
        pipelineSteps.append(stepProcessor)
        if category.type == StepType.CORE or category.type == StepType.PRE:
            processor : AbstractPipelineOption = stepProcessor(step.options.parameters)
            data = processor.fit_exec(data)

    pipeline = Pipeline(pipelineSteps)

    # pipeline.exec(datasets)

    assert(False)


def buildPipeline(req: PipelineRequest) -> Pipeline:
    options = []
    steps = []
    for step in req.selectedPipeline.steps:
        steps.append(getCategory(step.name))
        options.append(getPipelineOption(step.options.name)(step.options.parameters))
    return Pipeline(options, steps)

def getEvaluator(req: PipelineRequest) -> BaseEvaluation:
    evaluators = [x for x in req.selectedPipeline.steps if x.type == StepType.EVAL]
    if len(evaluators) > 1:
        raise Exception("Only one evaluator in a pipeline allowed")
    return getPipelineOption(evaluators[0].options.name)(evaluators[0].options.parameters)