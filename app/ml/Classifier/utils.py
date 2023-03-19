import numpy as np

def reshapeSklearn(data):
    print(data.shape)
    return np.reshape(data, (data.shape[0], np.multiply(*data.shape[1:])))