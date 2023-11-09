from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.BaseConfig import Platforms
import numpy as np
import json
from app.utils.jsonEncoder import JSONEncoder
from jinja2 import Template, FileSystemLoader
from app.Deploy.CPP.cPart import CPart
from app.ml.PipelineExport.C.Common.utils import getCode
from app.ml.PipelineExport.C.Common.Memory import Memory
from app.ml.PipelineExport.C.Common.CPart import CStep

class MinMaxNormalizer(BaseNormalizer):

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.min = None
        self.max = None

    @staticmethod
    def get_name():
        return "MinMaxNormalizer"

    @staticmethod
    def get_description():
        return "Normalizing the data to be in [0,1]"
    
    @staticmethod
    def config():
        return {"name": MinMaxNormalizer.get_name(), "parameters": {}}
    
    def fit_normalize(self, data):
        self.min = np.min(data, axis=0)
        self.max = np.max(data, axis=0)
        data = (data - self.min) / (self.max - self.min)
        return data

    def normalize(self, data):
        if self.min is None or self.max is None:
            raise Exception()
        return (data - self.min) / (self.max - self.min)
    
    def get_state(self):
        return {"min": json.dumps(self.min, cls=JSONEncoder), "max": json.dumps(self.max, cls=JSONEncoder)}

    def restore(self, config):
        self.min = np.array(json.loads(config.state["min"]))
        self.max = np.array(json.loads(config.state["max"]))
        super().restore(config)

    def export(self, params, platforms: Platforms):
        return self.exportC(params)

    @staticmethod
    def load(self, config):
        print(config)

    def _matrix_to_vector(self, data):
        code = "{\n"
        for row in data:
            code += "    {"
            code += ", ".join(str(x) for x in row)
            code += "},\n"
        code += "};"
        return code
    
    def exportC2(self, params):
        code = '''

        Matrix mins = {{min}}
        Matrix maxs = {{max}}

        void normalize(Matrix &input)
        {
            int num_sensors = input.size();
            int feature_size = input[0].size();
            for (int i = 0; i < num_sensors; i++)
            {
                for (int j = 0; j < feature_size; j++)
                {
                    input[i][j] = (input[i][j] - mins[i][j]) / (maxs[i][j] - mins[i][j]);
                }
            }
        }
        '''

        jinjaVars = {"min": self._matrix_to_vector(self.min), "max": self._matrix_to_vector(self.max)}

        return CPart([], [], code, jinjaVars)
    
    def exportC(self, params):

        variables = {"min": self._matrix_to_vector(self.min), "max": self._matrix_to_vector(self.max)}
        code = getCode("./app/ml/PipelineExport/C/Normalizer/MinMaxNormalizer.cpp")
        print("Normalizer: ", self.input_shape, self.output_shape)
        input_mem = self.input_shape
        output_Mem = self.output_shape
        step = CStep(variables, code, input_mem, output_Mem)
        return step