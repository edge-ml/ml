from app.ml.FeatureExtraction import BaseFeatureExtractor
import numpy as np
from jinja2 import Template


class SimpleFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self._FEATURES = [np.sum, np.median, np.mean, np.std, np.var, np.max, lambda x : np.abs(np.max(x)), np.min, lambda x : np.abs(np.min(x))]

    @staticmethod
    def get_name():
        return "SimpleFeatureExtractor"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_description():
        return "Extracts simple features form the incomming time-series windows"

    def _extract_features(self, data):
        return np.array([f(data) for f in self._FEATURES])

    def extract_features(self, windows, labels):
        window_features = []
        for w in windows:
            stack = []
            for i in range(1, windows.shape[-1]):
                stack.append(self._extract_features(w[:, i]))
            window_features.append(np.stack(stack))

        return np.array(window_features), labels

    def exportC(self):
        template = '''
        void extract_features(Matrix inputs, Matrix outputs)
        {

            for (int i = 0; i < NUM_SENSORS; i++)
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

        data = {}

        template = Template(template)
        return template.render(data)