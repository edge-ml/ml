

from app.codegen.inference import InferenceFormats
from app.internal.consts import SAMPLE_BASED_WINDOWING, TIME_BASED_WINDOWING
from app.utils.parameter_builder import ParameterBuilder

class Classifier:
    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
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
        pb.add_selection(
            "windowing_mode",
            "Windowing Mode",
            "Controls the interpretation of window size and sliding step parameters. With sample based windowing they are interpreted as number of samples, with time based windowing as time interval in milliseconds.",
            [SAMPLE_BASED_WINDOWING, TIME_BASED_WINDOWING],
            SAMPLE_BASED_WINDOWING,
            False,
            True,
            False
        )
        return pb.parameters

    @staticmethod
    def get_name():
        return "Edge Model Base"

    @staticmethod
    def get_description():
        return "Basic model that defines hyperparameters. Predicts random results based on class probability."

    @staticmethod
    def get_platforms():
        return []
    
    @staticmethod
    def config():
        raise NotImplementedError()

    # class methods
    def __init__(self, hyperparameters=[]):
        self.is_fit = False
        self._hyperparameters = hyperparameters


    def fit(self, X_train, y_train):
        raise NotImplementedError

    def predict(self, X_test):
        raise NotImplementedError

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error

    def export(self, platform: InferenceFormats): # https://github.com/nok/sklearn-porter#estimators (maybe?)
        raise NotImplementedError

    @property
    def hyperparameters(self):
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, value):
        self._hyperparameters = value
        params = {x["name"]: x["value"] for x in self._hyperparameters}
        self.clf.set_params(**params)

    def get_state():
        raise NotImplementedError()