from enum import Enum

class InferenceFormats(Enum):
    JAVASCRIPT = 'javascript', 'Model as javascript code' # https://github.com/BayesWitnesses/m2cgen
    PYTHON = 'python', 'Model as python code' # https://github.com/BayesWitnesses/m2cgen
    C = 'c', 'Model as C code' # https://github.com/BayesWitnesses/m2cgen
    C_EMBEDDED = 'c-embedded', 'Model as C code, low memory usage' # https://github.com/eloquentarduino/micromlgen
    ARDUINO_CPP ="arduino_cpp", "Model as Arduino Header file"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, description: str = None):
        self._description_ = description

    def __str__(self):
        return self.value

    # this makes sure that the description is read-only
    @property
    def description(self):
        return self._description_

    @staticmethod
    def from_str(label):
        try:
            return InferenceFormats(label.lower())
        except:
            raise NotImplementedError