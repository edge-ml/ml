
from app.ml.Pipelines.Abstract.AbstractPipelineStep import StepType, AbstractPipelineStep
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from typing import List, Union

# class Pipeline():

#     def __init__(self, windower: BaseWindower = None, featureExtractor: BaseFeatureExtractor = None, normalizer: BaseNormalizer = None, classifier: BaseClassififer = None, pipelineData: PipelineModel = None):
#         self.windower = windower
#         self.featureExtractor = featureExtractor
#         self.normalizer = normalizer
#         self.classifier = classifier
#         self.piplineData = pipelineData

#     def persist(self):
#         return {"windower": self.windower.persist(), "featureExtractor": self.featureExtractor.persist(), "normalizer": self.normalizer.persist(), "classifier": self.classifier.persist()}
    
#     @staticmethod
#     def get_parameters():
#         pb = ParameterBuilder()
#         pb.parameters = []
#         pb.add_number("Classification frequency", "Classification frequency", "Sets the frequncy in Hz to predict", 0.1, 10, 1, step_size=0.1, required=True, is_advanced=False)
#         # print(pb.parameters)
#         return pb.parameters

#     @staticmethod
#     def load(pipeline : PipelineModel):

#         classifier = get_classifier_by_name(pipeline.classifier.name)()
#         classifier.restore(pipeline.classifier)
#         normalizer = get_normalizer_by_name(pipeline.normalizer.name)()
#         normalizer.restore(pipeline.normalizer)
#         windower = get_windower_by_name(pipeline.windower.name)()
#         windower.restore(pipeline.windower)
#         featureExtractor = get_feature_extractor_by_name(pipeline.featureExtractor.name)()
#         featureExtractor.restore(pipeline.featureExtractor)

#         return Pipeline(windower, featureExtractor, normalizer, classifier, pipeline)
    

#     def generateModelData(self, platform: Platforms):
#         data = {}
#         data["windower"] = self.windower.export(platform)
#         data["featureExtractor"] = self.featureExtractor.export(platform)
#         data["normalizer"] = self.normalizer.export(platform)
#         data["classifier"] = self.classifier.export(platform)

#         if platform == Platforms.C:
#             return self.generateModelData_C(data)

#     def generateModelData_C(self, data):
#         with open('app/Deploy/Sklearn/Templates/CPP_Base.cpp') as f:
#             jinjaVars = {"includes": [], "globals": [], "labels": self.piplineData.labels, "samplingRate": self.piplineData.samplingRate}

#             functions = {"join": lambda x, y : f"{y}".join(x), "enumerate": enumerate}
#             additional_files = []

#             for (key, value) in data.items():
#                 jinjaVars[key] = value.code
#                 jinjaVars["includes"].extend(value.includes)
#                 jinjaVars["globals"].extend(value.globals)
#                 jinjaVars = {**jinjaVars, **value.jinjaVars}
#                 additional_files.extend(value.addtional_files)
#             template = Template(f.read())
#         res = template.render(jinjaVars, **functions) # Add code snippests to the template
#         res = Template(res).render(jinjaVars, **functions) # Populate the code snippets with the variables
#         main_file = StringFile(res, "model.hpp")
#         zip = zipFiles([main_file] + additional_files)
#         return zip


class Pipeline():
    
    def __init__(self, options, steps):
        self.options : List[AbstractPipelineOption] = options
        self.steps: List[AbstractPipelineStep] = steps

    def exec(self, data, types : Union[StepType, List[StepType]]):
        for step in self.options:
            if step.type in types:
                data = step.exec(data)
        return data
    
    def fit_exec(self, data, types: Union[StepType, List[StepType]]):
        print("TYPES: ", types)
        for step in self.options:
            print("STEP: ", step.get_name(), step.type)
            print(data.data.shape)
            if step.type in types:
                print("Fit_exec: ", step.get_name())
                data = step.fit_exec(data)
                print(step.get_name(), data)
        return data

    def clone(self):
        return Pipeline([x.__class__(x.parameters) for x in self.options])
    
    def __str__(self) -> str:
        return ", ".join([x.get_name() for x in self.options])
    
    def persist(self):
        return {"options": [x.persist() for x in self.options], "steps": [x.get_train_config() for x in self.steps]}