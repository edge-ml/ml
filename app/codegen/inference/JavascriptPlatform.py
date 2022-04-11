from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.InferenceFormats import InferenceFormats


class JavascriptPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Javascript"
    
    def supported_formats(self):
        return [InferenceFormats.JAVASCRIPT]

    def codegen(self, window_size, timeseries, labels, format):
        return "here's js code"