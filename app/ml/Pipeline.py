from app.ml.Windowing import BaseWindower
from app.ml.FeatureExtraction import BaseFeatureExtractor
from app.ml.Normalizer import BaseNormalizer
from app.ml.Classifier import BaseClassififer
from app.DataModels.PipeLine import PipelineModel
from app.ml.BaseConfig import Platforms
from app.Deploy.CPP.cPart import CPart
from app.utils.zipfile import zipFiles
from app.utils.StringFile import StringFile

from app.ml.Windowing import get_windower_by_name
from app.ml.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Classifier import get_classifier_by_name
from app.utils.parameter_builder import ParameterBuilder
from jinja2 import Template, FileSystemLoader
from io import BytesIO, StringIO
from typing import List

class Pipeline():

    def __init__(self, windower: BaseWindower = None, featureExtractor: BaseFeatureExtractor = None, normalizer: BaseNormalizer = None, classifier: BaseClassififer = None, pipelineData: PipelineModel = None):
        self.windower = windower
        self.featureExtractor = featureExtractor
        self.normalizer = normalizer
        self.classifier = classifier
        self.piplineData = pipelineData

    def persist(self):
        return {"windower": self.windower.persist(), "featureExtractor": self.featureExtractor.persist(), "normalizer": self.normalizer.persist(), "classifier": self.classifier.persist()}
    
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number("Classification frequency", "Classification frequency", "Sets the frequncy in Hz to predict", 0.1, 10, 1, step_size=0.1, required=True, is_advanced=False)
        # print(pb.parameters)
        return pb.parameters

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

        return Pipeline(windower, featureExtractor, normalizer, classifier, pipeline)
    

    def generateModelData(self, platform: Platforms):
        platform_for_parts = platform
        if platform == Platforms.WASM:
            platform_for_parts = Platforms.C

        data = {}
        data["windower"] = self.windower.export(platform_for_parts)
        data["featureExtractor"] = self.featureExtractor.export(platform_for_parts)
        data["normalizer"] = self.normalizer.export(platform_for_parts)
        data["classifier"] = self.classifier.export(platform_for_parts)

        if platform == Platforms.C:
            return self.generateModelData_C(data)
        elif platform == Platforms.WASM:
            return self.generateModelData_WASM(data)

    def generateModelData_CLike(self, data, base_template, out_name):
        with open(base_template) as f:
            jinjaVars = {"includes": [], "globals": [], "labels": self.piplineData.labels, "samplingRate": self.piplineData.samplingRate}

            functions = {"join": lambda x, y : f"{y}".join(x), "enumerate": enumerate}
            additional_files = []

            for (key, value) in data.items():
                jinjaVars[key] = value.code
                jinjaVars["includes"].extend(value.includes)
                jinjaVars["globals"].extend(value.globals)
                jinjaVars = {**jinjaVars, **value.jinjaVars}
                additional_files.extend(value.addtional_files)
            template = Template(f.read())
        res = template.render(jinjaVars, **functions) # Add code snippests to the template
        res = Template(res).render(jinjaVars, **functions) # Populate the code snippets with the variables
        main_file = StringFile(res, out_name)
        zip = zipFiles([main_file] + additional_files)
        return zip

    def generateModelData_C(self, data):
        return self.generateModelData_CLike(data, 'app/Deploy/Sklearn/Templates/CPP_Base.cpp', 'model.hpp')
    
    def generateModelData_WASM(self, data):
        return self.generateModelData_CLike(data, 'app/Deploy/Sklearn/Templates/WASM_Base.cpp', 'model.cpp')
        