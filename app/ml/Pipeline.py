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
from app.Deploy.Devices.BaseDevice import QuantizationLevels
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
        pb.add_selection("Quantization Method", "Quantization Method", "Choose which quantization method to be used", value=QuantizationLevels.NO_QUANT.value, options=[QuantizationLevels.NO_QUANT.value, QuantizationLevels.DYN_RANGE.value, QuantizationLevels.INT8.value], is_advanced=False)
        
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
    

    def generateModelData(self, platform: Platforms, quantization_level: QuantizationLevels = QuantizationLevels.NO_QUANT):
        data = {}
        data["windower"] = self.windower.export(platform)
        data["featureExtractor"] = self.featureExtractor.export(platform)
        data["normalizer"] = self.normalizer.export(platform)
        data["classifier"] = self.classifier.export(platform, quantization_level)
        if platform == Platforms.C:
            if self.classifier.is_neural_network():
                return self.generateModelData_NN(data)
            return self.generateModelData_C(data)

    def generateModelData_C(self, data):
        with open('app/Deploy/Sklearn/Templates/CPP_Base.cpp') as f:
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
        main_file = StringFile(res, "model.hpp")
        zip = zipFiles([main_file] + additional_files)
        return zip
    
    def generateModelData_NN(self, data):
        model_data = StringFile(data["classifier"], "model_data.hpp")
        normalizer = Template(data["normalizer"].code).render(data["normalizer"].jinjaVars)
        normalizer = StringFile(normalizer, "normalizer.hpp")
        windower = Template(data["windower"].code).render(data["windower"].jinjaVars)
        windower = StringFile(windower, "windower.hpp")
        
        with open('app/Deploy/Tensorflow/Templates/Prediction.cpp') as f:
            predictor = Template(f.read()).render({"labels": self.piplineData.labels, "samplingRate": self.piplineData.samplingRate})
            predictor = StringFile(predictor, "predictor.hpp")
        
        zip = zipFiles([model_data, normalizer, windower, predictor])
        return zip