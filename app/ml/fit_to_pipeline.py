import numpy as np
from typing import Tuple
from app.DataModels.trainRequest import TrainRequest
from app.ml.Classifier import get_classifier_by_name
from app.ml.Evaluation import BaseEvaluation, get_eval_by_name
from app.ml.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Pipeline import Pipeline
from app.ml.Windowing import get_windower_by_name

def fit_to_pipeline(trainReq : TrainRequest, datasets, labels) -> Tuple[Pipeline, BaseEvaluation]:
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