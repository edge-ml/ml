from app.ml.BaseConfig import BaseConfig

class BaseWindower(BaseConfig):

    def __init__(self, parameters):
        super().__init__(parameters)

    def window(self, datasets):
        raise NotImplementedError()