from app.ml.Windowing.BaseWindower import BasicWindower
from app.utils.parameter_builder import ParameterBuilder

class TimeWindower(BasicWindower):

    def __init__(self, hyperparameters):
        super().__init__(hyperparameters)

    @staticmethod
    def get_name():
        return "Time based"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_description():
        return "Windowing, where each window has the same length in the temporal dimension"

    @staticmethod
    def config():
        return {
        "name": TimeWindower.get_name(),
        "description": TimeWindower.get_description(),
        "parameters": TimeWindower.get_hyperparameters(),
        "platforms": TimeWindower.get_platforms()
        }

    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
        print(pb.parameters)
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

        print(pb.parameters)
        return pb.parameters


    def window():
        raise NotImplementedError()