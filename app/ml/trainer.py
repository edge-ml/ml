import numpy as np


from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset
from time import sleep

from app.models.decision_tree import DecisionTree
from app.models.decision_tree import DecisionTree
from app.models.random_forest import RandomForest

from app.DataProcessor.DataPreProcessor import getDatasetWindows, extract_features
from app.DataProcessor.DataLoader import processDataset

EDGE_MODELS = [RandomForest, DecisionTree, DecisionTree]



# def processDataset(dataset, labeling_id, labelMap):
    
#     # Get labels in datasets
#     labels = [x for x in dataset.labelings if x.labelingId == labeling_id][0].labels
#     # Get the time-series
#     dfs = []
    
#     for ts in dataset.timeSeries:
#         binStore = BinaryStore(ts.id)
#         binStore.loadSeries()
#         ts_data = binStore.getFull()
#         data = ts_data["data"]
#         time = ts_data["time"]
#         df = pd.DataFrame({"time": time, ts.name: data})
#         dfs.append(df)


#     # Merge the dataframes
#     df = dfs[0]
#     for d in dfs[1:]:
#         df = pd.merge(df, d, how='outer', on="time")

#     df = df.interpolate(method='linear', limit_direction='both')
    
#     dims = df.columns
#     arr = df.to_numpy()
#     label_arr = np.empty((arr.shape[0], 1))

#     arr = np.concatenate([arr, label_arr], axis=1)

#     for i, t in enumerate(arr):
#         for l in labels:
#             if t[0] >= int(l.start) and t[0] <= int(l.end):
#                 arr[i][-1] = labelMap[str(l.type)]
#                 break
#             else:
#                 arr[i][-1] = 0
    
#     return arr

# def getDatasetWindows(dataset, window_size, stride):
#     window_size = 100
#     stride = 20

#     fused = []
#     idx = 0
#     while idx < dataset.shape[0]:
#         if idx+window_size > dataset.shape[0]:
#             break
#         fused.append(dataset[idx: idx+window_size])
#         idx += stride

#     labels = []
#     windows = []

#     for w in fused:
#         windows.append(w[:, :-1])
#         counts = np.bincount(w[:,-1].astype(int))
#         label = np.argmax(counts)
#         labels.append(label)

#     windows = np.array(windows)
#     labels = np.array(labels)
#     return windows, labels


# features = [np.sum, np.median, np.mean, np.std, np.var, np.max, lambda x : np.abs(np.max(x)), np.min]

# def extract_features(data):
#     return np.array([f(data) for f in features])


# def calculateFeatures(windows):
#     window_features = []
#     for w in windows:
#         stack = []
#         for i in range(1, windows.shape[-1]):
#             stack.append(extract_features(w[:, i]))
#         window_features.append(np.stack(stack))

#     return np.array(window_features)    


# def trainClassifier(windows, labels):
#     clf = DecisionTreeClassifier()
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf

# def calculateMetrics(self, y_test, y_pred):
#     metrics = {}
#     metrics['accuracy_score'] = accuracy_score(y_test, y_pred)
#     metrics['precision_score'] = precision_score(y_test, y_pred, average='weighted')
#     metrics['recall_score'] = recall_score(y_test, y_pred, average='weighted')
#     metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted')
#     num_labels = [float(idx) for idx, label in enumerate(self.labels)]
#     target_names = self.labels
#     if self.use_unlabelled:
#         num_labels.append(float(len(num_labels)))
#         target_names.append(self.unlabelled_name)
#     metrics['confusion_matrix'] = array2string(confusion_matrix(y_test, y_pred, labels=num_labels))
#     metrics['classification_report'] = classification_report(y_test, y_pred, labels=num_labels, zero_division=0, target_names=target_names)
#     return metrics


async def init_train(trainReq, id, project):
    await update_model_status(id, project, ModelStatus.preprocessing)

    # Get the datasets and lableings used for training
    datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
    labeling = await get_labeling(trainReq.labeling, project)
    
    labelMap = {str(x.id): i+1 for i, x in enumerate(labeling.labels)}
    print(labelMap)

    all_windows = []
    all_labels = []
    sleep(3)
    for dataset in datasets:
        arr = processDataset(dataset, trainReq.labeling, labelMap)
        windows, labels = getDatasetWindows(arr, window_size=50, stride=20)
        windows = calculateFeatures(windows)
        print(windows.shape)
        all_windows.append(windows)
        all_labels.extend(labels)

    all_windows = np.concatenate(all_windows, axis=0)
    all_labels = np.array(all_labels)

    filter = np.array([x > 0 for x in all_labels])

    all_windows = all_windows[filter]
    all_labels = all_labels[filter]
    sleep(3)
    await update_model_status(id, project, ModelStatus.fitting_model)
    clf = trainClassifier(all_windows, all_labels)
    sleep(3)
    await update_model_status(id, project, ModelStatus.evaluating)



    return clf

async def train(trainReq, project, background_tasks):
    data = trainReq.dict(by_alias=True)
    storedHyperparameters = [{"name": str(x["name"]), "value": str(x["value"])} for x in trainReq.modelInfo.hyperparameters]
    model = Model(name = trainReq.name, hyperparameters=storedHyperparameters, classifier=trainReq.modelInfo.classifier, labeling=trainReq.labeling, datasets=data["datasets"], projectId=project)
    id = await add_model(model=model.dict(by_alias=True))
    background_tasks.add_task(init_train, trainReq, id, project)
    return id