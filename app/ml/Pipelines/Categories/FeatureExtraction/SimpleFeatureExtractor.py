from app.ml.Pipelines.Categories.FeatureExtraction import BaseFeatureExtractor
import numpy as np
from app.Deploy.CPP.cPart import CPart
from app.utils.StringFile import StringFile
from app.ml.PipelineExport.C.Common.utils import getCode
from app.ml.PipelineExport.C.Common.Memory import Memory
from app.ml.PipelineExport.C.Common.CPart import CStep, ExtraFile
from app.ml.BaseConfig import Platforms


class SimpleFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self._FEATURES = [np.sum, np.median, np.mean, np.std, np.var, np.max, lambda x : np.abs(np.max(x)), np.min, lambda x : np.abs(np.min(x))]

    @staticmethod
    def get_name():
        return "SimpleFeatureExtractor"

    @staticmethod
    def get_platforms():
        return [Platforms.C]

    @staticmethod
    def get_description():
        return "Extracts simple features form the incomming time-series windows"

    def _extract_features(self, data):
        return np.array([f(data) for f in self._FEATURES])

    def extract_features(self, windows):
        print("Feature_extractor: ")
        print(windows.shape)
        window_features = []
        for w in windows:
            stack = []
            for i in range(1, w.shape[-1]):
                stack.append(self._extract_features(w[:, i]))
            window_features.append(np.stack(stack))
        return np.array(window_features)

    def export(self, params, platform):
        return self.exportC(params)

    def exportC(self, params):
        code = getCode("./app/ml/PipelineExport/C/FeatureExtractor/SimpleFeatureExtractor.cpp")
        input_shape = self.input_shape
        output_shape = self.output_shape

        with open("./app/ml/Pipelines/Categories/FeatureExtraction/feature_extractor.hpp", "r") as f:
            extraFile = ExtraFile("feature_extractor.hpp", f.read())
        return CStep({}, code, input_shape, output_shape, includes=['#include "feature_extractor.hpp"'], extra_files=[extraFile])

        


    def exportC2(self, params):
        code = '''
        void extract_features(Matrix &inputs, Matrix &outputs)
        {

            for (int i = 0; i < {{num_sensors}}; i++)
            {
                outputs[i][0] = sum(inputs[i]);
                outputs[i][1] = median(inputs[i]);
                outputs[i][2] = mean(inputs[i]);
                outputs[i][3] = standard_deviation(inputs[i]);
                outputs[i][4] = variance(inputs[i]);
                outputs[i][5] = max(inputs[i]);
                outputs[i][6] = abs_max(inputs[i]);
                outputs[i][7] = min(inputs[i]);
                outputs[i][8] = abs_min(inputs[i]);
            }
        }
        '''
        
        with open("./app/ml/FeatureExtraction/feature_extractor.hpp", "r") as f:
            feature_extractor_file = [StringFile(f.read(), f.name.split("/")[-1])]


        return CPart(['#include "feature_extractor.hpp"'], ["Matrix features({{num_sensors}}, std::vector<float>({{num_features}}));"], code, {"num_features": len(self._FEATURES)}, feature_extractor_file)
