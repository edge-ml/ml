from enum import Enum

class StepType(str, Enum):
    CORE = "CORE"
    INFO = "INFO"
    EVAL = "EVAL"
    PRE = "PRE"
