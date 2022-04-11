from enum import Enum

class InferenceFormats(Enum):
    JAVASCRIPT = 'javascript', 'Model as javascript code' # https://github.com/BayesWitnesses/m2cgen
    PYTHON = 'python', 'Model as python code' # https://github.com/BayesWitnesses/m2cgen
    C = 'c', 'Model as C code' # https://github.com/BayesWitnesses/m2cgen
    C_EMBEDDED = 'c-embedded', 'Model as C code, low memory usage' # https://github.com/eloquentarduino/micromlgen

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
        if label.lower() == 'javascript':
            return InferenceFormats.JAVASCRIPT
        if label.lower() == 'python':
            return InferenceFormats.PYTHON
        elif label.lower() == 'c':
            return InferenceFormats.C
        elif label.lower() == 'c-embedded':
            return InferenceFormats.C_EMBEDDED
        else:
            raise NotImplementedError