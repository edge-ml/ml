from app.ml.Windowing import BaseWindower
from app.ml.FeatureExtraction import BaseFeatureExtractor
from app.ml.Normalizer import BaseNormalizer
from app.ml.Classifier import BaseClassififer
from app.DataModels.PipeLine import PipelineModel
from app.ml.BaseConfig import Platforms
from app.Deploy.CPP.cPart import CPart

from app.ml.Windowing import get_windower_by_name
from app.ml.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Classifier import get_classifier_by_name
from jinja2 import Template, FileSystemLoader

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

        classifier = get_classifier_by_name(pipeline.classifier.name)()
        classifier.restore(pipeline.classifier)
        normalizer = get_normalizer_by_name(pipeline.normalizer.name)()
        normalizer.restore(pipeline.normalizer)
        windower = get_windower_by_name(pipeline.windower.name)()
        windower.restore(pipeline.windower)
        featureExtractor = get_feature_extractor_by_name(pipeline.featureExtractor.name)()
        featureExtractor.restore(pipeline.featureExtractor)

        return Pipeline(windower, featureExtractor, normalizer, classifier)
    

    def deploy(self, platform: Platforms):
        data = {}
        data["windower"] = self.windower.export(platform)
        data["featureExtractor"] = self.featureExtractor.export(platform)
        data["normalizer"] = self.normalizer.export(platform)
        data["classifier"] = self.classifier.export(platform)

        if platform == Platforms.C:
            return self.deployC(data)

    def deployC(self, data):
        with open('app/Deploy/Sklearn/Templates/CPP_Base.jinja') as f:
            jinjaVars = {"includes": [], "globals": []}

            functions = {"join": lambda x, y : f"{y}".join(x)}


            for (key, value) in data.items():
                jinjaVars[key] = value.code
                jinjaVars["includes"].extend(value.includes)
                jinjaVars["globals"].extend(value.globals)
                jinjaVars = {**jinjaVars, **value.jinjaVars}
            template = Template(f.read())
        res = template.render(jinjaVars, **functions) # Add code snippests to the template
        res = Template(res).render(jinjaVars, **functions) # Populate the code snippets with the variables
        return res