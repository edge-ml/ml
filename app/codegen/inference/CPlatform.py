from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.InferenceFormats import InferenceFormats

class CPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "C"
    
    def supported_formats(self):
        return [InferenceFormats.C, InferenceFormats.C_EMBEDDED]

    def codegen(self, window_size, timeseries, labels, format):
        return "here's c code"