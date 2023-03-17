import numpy as np

FEATURES = [np.sum, np.median, np.mean, np.std, np.var, np.max, lambda x : np.abs(np.max(x)), np.min]

def getDatasetWindows(dataset, window_size, stride):
    window_size = 100
    stride = 20

    fused = []
    idx = 0
    while idx < dataset.shape[0]:
        if idx+window_size > dataset.shape[0]:
            break
        fused.append(dataset[idx: idx+window_size])
        idx += stride

    labels = []
    windows = []

    for w in fused:
        windows.append(w[:, :-1])
        counts = np.bincount(w[:,-1].astype(int))
        label = np.argmax(counts)
        labels.append(label)

    windows = np.array(windows)
    labels = np.array(labels)
    return windows, labels

def extract_features(data):
    return np.array([f(data) for f in FEATURES])


def calculateFeatures(windows):
    window_features = []
    for w in windows:
        stack = []
        for i in range(1, windows.shape[-1]):
            stack.append(extract_features(w[:, i]))
        window_features.append(np.stack(stack))

    return np.array(window_features)    