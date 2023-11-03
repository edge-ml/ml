import numpy as np
from typing import Tuple
from app.DataModels.trainRequest import TrainRequest
from app.ml.Pipelines.Categories.Classifier import get_classifier_by_name
from app.ml.Pipelines.Categories.Evaluation import BaseEvaluation, get_eval_by_name
from app.ml.Pipelines.Categories.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Pipelines.Categories.Normalizer import get_normalizer_by_name
from app.ml.Pipeline import Pipeline
from app.ml.Pipelines.Categories.Windowing import get_windower_by_name
from app.DataModels.PipelineRequest import PipelineRequest
from app.ml.Pipelines import getProcessor, getCategory
from app.ml.Pipelines.Abstract.AbstractPipelineStep import StepType
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption

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
        print(category.name, category.type)
        stepProcessor = getProcessor(step.options.name)
        print(stepProcessor)
        pipelineSteps.append(stepProcessor)
        if category.type == StepType.CORE or category.type == StepType.PRE:
            processor : AbstractPipelineOption = stepProcessor(step.options.parameters)
            data = processor.fit_exec(data)

    pipeline = Pipeline(pipelineSteps)

    # pipeline.exec(datasets)

    assert(False)