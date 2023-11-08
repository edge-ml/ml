from app.ml.Windowing.BaseWindower import BaseWindower
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


    def window(self, datasets):
        window_size = int(self.get_param_value_by_name("window_size"))
        stride = int(self.get_param_value_by_name("sliding_step"))
        train_X = []
        train_Y = []
        for dataset in datasets:
            fused = []
            idx = 0
            while idx < dataset.shape[0]:
                if idx+window_size > dataset.shape[0]:
                    break
                fused.append(dataset[idx: idx+window_size])
                idx += stride

            X = []
            Y = []

            for w in fused:
                X.append(w[:, :-1])
                counts = np.bincount(w[:,-1].astype(int))
                label = np.argmax(counts)
                Y.append(label)

            train_X.extend(np.array(X))
            train_Y.extend(np.array(Y))
            # print("PRE - filter")
            # print(train_Y)
        return self._filterLabelings(np.array(train_X), np.array(train_Y))

    def exportC(self):
        # TODO: these params should be saved as integers in the first place
        global_vars = {"window_size": int(self.get_param_value_by_name("window_size")), "sliding_step": int(self.get_param_value_by_name("sliding_step"))}


        # code = '''
        # void add_datapoint({{timeSeriesInput}})
        #     {
        #         {% for ts in timeSeries %}
        #             raw_data[{{loop.index-1}}][ctr] = {{ts}};
        #         {% endfor %}
        #         ctr++;
        #         if (ctr >= {{window_size}})
        #         {
        #             ctr = 0;
        #         }
        #     }
        # '''
        
        code = '''constexpr int window_size = {{window_size}};
constexpr int sensor_stream_count = {{timeSeries|length}};
float data_window[window_size * sensor_stream_count] = {0};
int data_count = 0;

void addDataPoint(float *data) {
  if (data_count < window_size) {
    for (int i = 0; i < sensor_stream_count; i++) {
      data_window[data_count * sensor_stream_count + i] = data[i]; 
    }
    data_count++;
  } else {
    // Slide the window
    for (int i = 0; i < window_size; i++) {
      for (int j = 0; j < sensor_stream_count; j++) {
        data_window[i * sensor_stream_count + j] = (i != window_size - 1) ? data_window[(i+1) * sensor_stream_count + j] : data[j];
      }
    }
  }
}
        '''
        
        timeSeries = ["x", "y", "z"]
        jinjaVars = {"timeSeries": timeSeries, "timeSeriesInput": ",".join([f"float {x}" for x in timeSeries]), "num_sensors": len(timeSeries), **global_vars}

        return CPart([], ["Matrix raw_data({{num_sensors}}, vector<float>({{window_size}}));", "int ctr = 0;"], code, jinjaVars)