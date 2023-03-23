from app.ml.Windowing.BaseWindower import BasicWindower
from app.utils.parameter_builder import ParameterBuilder
import numpy as np

class SampleWindower(BasicWindower):

    def __init__(self, hyperparameters):
        super().__init__(hyperparameters)

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
    def config():
        return {
        "name": SampleWindower.get_name(),
        "description": SampleWindower.get_description(),
        "parameters": SampleWindower.get_hyperparameters(),
        "platforms": SampleWindower.get_platforms()
        }

    @staticmethod
    def get_hyperparameters():
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


    def window(self, datasets):
        window_size = self.hyperparameters[0]["value"]
        stride = self.hyperparameters[1]["value"]
        all_windows = []
        all_labels = []
        for dataset in datasets:
            fused = []
            idx = 0
            while idx < dataset.shape[0]:
                if idx+window_size > dataset.shape[0]:
                    break
                fused.append(dataset[idx: idx+window_size])
                idx += stride

            labels = []
            windows = []

            for w in fused:
                windows.append(w[:, :-1])
                counts = np.bincount(w[:,-1].astype(int))
                label = np.argmax(counts)
                labels.append(label)

            all_windows.extend(np.array(windows))
            all_labels.extend(np.array(labels))
            
        return np.array(all_windows), np.array(all_labels)