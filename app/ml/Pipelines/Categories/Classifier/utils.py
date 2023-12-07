import numpy as np

def reshapeSklearn(data):
    return np.reshape(data, (data.shape[0], np.multiply(*data.shape[1:])))

def reshapeCNN(X):
    return X.reshape(X.shape[0], X.shape[1], X.shape[2], 1)