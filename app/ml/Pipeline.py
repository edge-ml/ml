from app.ml.Windowing import BaseWindower
from app.ml.FeatureExtraction import BaseFeatureExtractor
from app.ml.Normalizer import BaseNormalizer
from app.ml.Classifier import BaseClassififer
from app.DataModels.PipeLine import PipelineModel

from app.ml.Windowing import get_windower_by_name
from app.ml.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Classifier import get_classifier_by_name

class Pipeline():

    def __init__(self, windower: BaseWindower = None, featureExtractor: BaseFeatureExtractor = None, normalizer: BaseNormalizer = None, classifier: BaseClassififer = None):
        self.windower = windower
        self.featureExtractor = featureExtractor
        self.normalizer = normalizer
        self.classifier = classifier

    def persist(self):
        return {"windower": self.windower.persist(), "featureExtractor": self.featureExtractor.persist(), "normalizer": self.normalizer.persist(), "classifier": self.classifier.persist()}

    @staticmethod
    def load(pipeline : PipelineModel):

        classifier = get_classifier_by_name(pipeline.classifier.name)(pipeline.classifier.parameters)
        classifier.restore(pipeline.classifier.state)
        normalizer = get_normalizer_by_name(pipeline.normalizer.name)(pipeline.normalizer.parameters)
        normalizer.restore(pipeline.classifier.state)
        windower = get_windower_by_name(pipeline.windower.name)(pipeline.windower.parameters)
        windower.restore(pipeline.windower.state)
        featureExtractor = get_feature_extractor_by_name(pipeline.featureExtractor.name)(pipeline.featureExtractor.parameters)
        featureExtractor.restore(pipeline.featureExtractor.state)

        pipeline = Pipeline(windower, featureExtractor, normalizer, classifier)