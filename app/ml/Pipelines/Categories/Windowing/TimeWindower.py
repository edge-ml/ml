from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.utils.parameter_builder import ParameterBuilder
import numpy as np
from app.ml.BaseConfig import Platforms
from jinja2 import Template
from app.Deploy.CPP.cPart import CPart

class TimeWindower(BaseWindower):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "Time based"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_description():
        return "Windowing, where each window has the same length in the temporal dimension"

    def restore(self, config):
        self.parameters = config.parameters

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        # print(pb.parameters)
        pb.add_number(
            "window_size", "Window Size", "The window size sind milliseconds.", 0, 60000, 100, 1, True, False, False
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

        # print(pb.parameters)
        return pb.parameters

    def window(self, datasets):
        window_size = int(self.get_param_value_by_name("window_size"))
        stride = int(self.get_param_value_by_name("sliding_step"))
        train_X = []
        train_Y = []
        for dataset in datasets:
            dataset = dataset[dataset[:, 0].argsort()]
            window_start = dataset[0][0]
            fused = []
            idx = 0
            while idx < dataset.shape[0]:
                end_idx, next_idx = np.searchsorted(dataset[:, 0], [window_start + window_size, window_start + stride])
                if end_idx > dataset.shape[0]:
                    break
                fused.append(dataset[idx: end_idx])
                idx = next_idx
                window_start += stride

            # np.set_printoptions(precision=16)
            # for x in fused[:-10]:
            #     print(x[:, 0])

            X = []
            Y = []

            fused_cnt = np.array([len(w) for w in fused])
            
            if sum(fused_cnt == 0) > fused_cnt.shape[0] / 2:
                raise Exception("Too many empty windows, please adjust window size and sliding step.")
            
            for w in fused:
                if len(w) == 0:
                    continue
                X.append(w[:, :-1])
                counts = np.bincount(w[:,-1].astype(int))
                label = np.argmax(counts)
                Y.append(label)

            train_X.extend(X)
            train_Y.extend(Y)
            print("PRE - filter")
            print(train_Y)
        return self._filterLabelings(np.array(train_X, dtype=object), np.array(train_Y))

    def exportC(self):
        global_vars = {"window_size": int(self.get_param_value_by_name("window_size")), "sliding_step": int(self.get_param_value_by_name("sliding_step"))}


        code = '''
        void add_datapoint({{timeSeriesInput}})
            {
                unsigned long now = millis();
                unsigned long cutoff = now - {{window_size}};

                int cuttop = 0;
                while (cuttop < timestamps.size()) {
                    if (timestamps[cuttop] >= cutoff) {
                        break;
                    }
                    cuttop++;
                }

                if (cuttop) {
                    timestamps.erase(timestamps.begin(), timestamps.begin() + cuttop);
                    {% for ts in timeSeries %}
                        raw_data[{{loop.index-1}}].erase(raw_data[{{loop.index-1}}].begin(), raw_data[{{loop.index-1}}].begin() + cuttop);
                    {% endfor %}
                }

                timestamps.push_back(now);
                {% for ts in timeSeries %}
                    raw_data[{{loop.index-1}}].push_back({{ts}});
                {% endfor %}
            }
        '''
        timeSeries = ["x", "y", "z"]
        jinjaVars = {"timeSeries": timeSeries, "timeSeriesInput": ",".join([f"float {x}" for x in timeSeries]), "num_sensors": len(timeSeries), **global_vars}

        return CPart(["#include \"limits.h\""], ["Matrix raw_data({{num_sensors}}, vector<float>());", "vector<unsigned long> timestamps;", "unsigned long last_window_start = 0;"], code, jinjaVars)