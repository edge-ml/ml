from app.ml.BaseConfig import BaseConfig
import numpy as np

class BaseWindower(BaseConfig):

    def __init__(self, parameters):
        super().__init__(parameters)

    def window(self, datasets):
        raise NotImplementedError()

    def _filterLabelings(self, train_X, train_Y):
        filter = np.array([x != 9*10^10 for x in train_Y])
        print(train_Y)
        print(filter)
        train_X = train_X[filter]
        train_Y = train_Y[filter]
        return train_X, train_Y