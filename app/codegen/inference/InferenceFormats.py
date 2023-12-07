from enum import Enum

class InferenceFormats(str, Enum):
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    C = "c"
    C_EMBEDDED = "c-embedded"
    CPP ="cpp"

    def __new__(cls, *args, **kwds):
        obj = str.__new__(cls, args[0])
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