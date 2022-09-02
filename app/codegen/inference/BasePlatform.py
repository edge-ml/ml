from typing import List

from app.codegen.inference.InferenceFormats import InferenceFormats

class BasePlatform:
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def supported_formats(self) -> List[InferenceFormats]:
        raise NotImplementedError

    ###
    # Frontend needs to do some text replacement on the result:
    # ___DOWNLOADED_MODEL_BASENAME___ : basename of the downloaded model file (no extension)
    # ___DOWNLOADED_MODEL_NAME___ : name of the downloaded model file
    def codegen(self, window_size, timeseries, labels, format, scaler, windowing_mode):
        raise NotImplementedError