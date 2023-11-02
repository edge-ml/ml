from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.utils.parameter_builder import ParameterBuilder
import numpy as np
from app.ml.BaseConfig import Platforms
from jinja2 import Template
from app.Deploy.CPP.cPart import CPart

class SampleWindower(BaseWindower):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "Sample based"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_description():
        return "Sample based windowing using a sliding window approach"

    def fit_exec(self, data):
        return self.window(data)
    
    def exec(self, data):
        return self.exec(data)

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number(
            "window_size", "Window Size", "Sets the window size.", 0, 60000, 100, 1, True, False, False
        )
        pb.add_number(
            "sliding_step",
            "Sliding Step",
            "Sets how many steps the sliding window will slide. If it's set less than the window size, the windows will overlap.",
            1,
            60000,
            50,
            1,
            True,
            False,
            False
        )
        return pb.parameters
    
    def restore(self, config):
        self.parameters = config.parameters


    def window(self, data):
        datasets = data["datasets"]
        datasetMetadata = data["datasetMetadata"]
        window_size = int(self.get_param_value_by_name("window_size"))
        stride = int(self.get_param_value_by_name("sliding_step"))
        train_X = []
        train_Y = []
        metadata = []
        for dataset in datasets:
            print("Dataset_shape: ", dataset.shape)
            fused = []
            idx = 0
            while idx < dataset.shape[0]:
                if idx+window_size > dataset.shape[0]:
                    break
                fused.append(dataset[idx: idx+window_size])
                idx += stride

            X = []
            Y = []
            Meta = []

            for w in fused:
                X.append(w[:, :-1])
                counts = np.bincount(w[:,-1].astype(int))
                label = np.argmax(counts)
                Y.append(label)
                Meta.append(datasetMetadata)

            train_X.extend(X)
            train_Y.extend(Y)
            metadata.extend(Meta)
            
            print("PRE - filter")
            print(train_Y)
        return self._filterLabelings(np.array(train_X, dtype=object), np.array(train_Y), metadata)

    def exportC(self):
        global_vars = {"window_size": int(self.get_param_value_by_name("window_size")), "sliding_step": int(self.get_param_value_by_name("sliding_step"))}


        code = '''
        void add_datapoint({{timeSeriesInput}})
            {
                {% for ts in timeSeries %}
                    raw_data[{{loop.index-1}}][ctr] = {{ts}};
                {% endfor %}
                ctr++;
                if (ctr >= {{window_size}})
                {
                    ctr = 0;
                }
            }
        '''
        timeSeries = ["x", "y", "z"]
        jinjaVars = {"timeSeries": timeSeries, "timeSeriesInput": ",".join([f"float {x}" for x in timeSeries]), "num_sensors": len(timeSeries), **global_vars}

        return CPart([], ["Matrix raw_data({{num_sensors}}, vector<float>({{window_size}}));", "int ctr = 0;"], code, jinjaVars)