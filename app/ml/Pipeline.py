from app.ml.Windowing import BaseWindower
from app.ml.FeatureExtraction import BaseFeatureExtractor
from app.ml.Normalizer import BaseNormalizer
from app.ml.Classifier import BaseClassififer
from app.DataModels.PipeLine import PipelineModel


class Pipeline():

    def __init__(self, windower: BaseWindower = None, featureExtractor: BaseFeatureExtractor = None, normalizer: BaseNormalizer = None, classifier: BaseClassififer = None):
        self.windower = windower
        self.featureExtractor = featureExtractor
        self.normalizer = normalizer
        self.classifier = classifier

    def persist(self):
        return {"windower": self.windower.persist(), "featureExtractor": self.featureExtractor.persist(), "normalizer": self.normalizer.persist(), "classifier": self.classifier.persist()}

    def load(self, pipeline : PipelineModel):
        self.windower = pipeline.windower
        self.featureExtractor = pipeline.featureExtractor
        self.normalizer = pipeline.normalizer
        self.classifier = pipeline.classifier