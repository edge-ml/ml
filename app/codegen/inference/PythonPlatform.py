from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.internal.consts import SAMPLE_BASED_WINDOWING

def formatimport(format):
    if format == InferenceFormats.PYTHON:
        return "from ___DOWNLOADED_MODEL_BASENAME___ import score"
    else:
        return "predict = # load predict method somehow"

def formatmethod(format):
    if format == InferenceFormats.PYTHON:
        return "score(input)"
    else:
        return "predict(input)"
    

class PythonPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Python"
    
    def supported_formats(self):
        return [InferenceFormats.PYTHON]

    def codegen(self, window_size, timeseries, labels, format, scaler, windowing_mode):
        tadd = ""
        for ts in timeseries:
            tadd = tadd + '\n    p.add_datapoint(\'{ts}\', get{ts}())'.format(ts = ts)

        return """import time
from edgeml.predictor import Predictor, PredictorError

{importer}

p = Predictor(
    predictor = lambda input: {method},
    sensors = {timeseries_list},
    window_size = {wsize},
    labels = {labels},
    scaler = {scaler},
    windowing_mode = "{wmode}"
)

while True:{timeseries_add}

    try:
        print(p.predict())
    except PredictorError:
        pass
    
    time.sleep(0.25)
""".format(
            wsize=window_size,
            timeseries_list=str(timeseries),
            labels=str(labels),
            timeseries_add=tadd,
            importer=formatimport(format),
            method=formatmethod(format),
            scaler=scaler,
            wmode="sample" if windowing_mode == SAMPLE_BASED_WINDOWING else "time"
        )