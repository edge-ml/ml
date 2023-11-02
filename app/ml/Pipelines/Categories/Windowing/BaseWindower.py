from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep
import numpy as np

class BaseWindower(AbstractPipelineStep):

    def __init__(self, parameters):
        super().__init__(parameters)

    def window(self, datasets):
        raise NotImplementedError()

    def _filterLabelings(self, train_X, train_Y, metaData):
        filter = np.array([x != 9*10^10 for x in train_Y])
        # print(train_Y)
        # print(filter)
        train_X = train_X[filter]
        train_Y = train_Y[filter]
        metaData = [x for x, y in zip(metaData, filter) if y == 1]
        return train_X, train_Y, metaData