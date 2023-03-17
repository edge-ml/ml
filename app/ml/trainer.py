from typing import Any
import uuid
import numpy as np
from dataclasses import dataclass, field
import pandas as pd
from numpy import array2string
import tsfresh
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import ( 
    accuracy_score, 
    confusion_matrix, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report
)
from app.internal.consts import SAMPLE_BASED_WINDOWING

from app.internal.data_preparation import (
    extract_labels,
    create_dataframes,
    interpolate_values,
    label_dataset,
    merge_dataframes,
    roll_sliding_window,
)

from app.ml.training_state import TrainingState
from app.validation import ValidationBody
from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset
from app.db.binStore.binaryStore import BinaryStore

from sklearn.tree import DecisionTreeClassifier

def processDataset(dataset, labeling_id, labelMap):
    
    # Get labels in datasets
    labels = [x for x in dataset.labelings if x.labelingId == labeling_id][0].labels
    # Get the time-series
    dfs = []
    
    for ts in dataset.timeSeries:
        binStore = BinaryStore(ts.id)
        binStore.loadSeries()
        ts_data = binStore.getFull()
        data = ts_data["data"]
        time = ts_data["time"]
        df = pd.DataFrame({"time": time, ts.name: data})
        dfs.append(df)


    # Merge the dataframes
    df = dfs[0]
    for d in dfs[1:]:
        df = pd.merge(df, d, how='outer', on="time")

    df = df.interpolate(method='linear', limit_direction='both')
    
    dims = df.columns
    arr = df.to_numpy()
    label_arr = np.empty((arr.shape[0], 1))

    arr = np.concatenate([arr, label_arr], axis=1)

    for i, t in enumerate(arr):
        for l in labels:
            if t[0] >= int(l.start) and t[0] <= int(l.end):
                arr[i][-1] = labelMap[str(l.type)]
                break
            else:
                arr[i][-1] = 0
    
    return arr

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


features = [np.sum, np.median, np.mean, np.std, np.var, np.max, lambda x : np.abs(np.max(x)), np.min]

def extract_features(data):
    return np.array([f(data) for f in features])


def calculateFeatures(windows):
    window_features = []
    for w in windows:
        stack = []
        for i in range(1, windows.shape[-1]):
            stack.append(extract_features(w[:, i]))
        window_features.append(np.stack(stack))

    return np.array(window_features)    


def trainClassifier(windows, labels):
    clf = DecisionTreeClassifier()
    windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
    clf.fit(windows, labels)
    return clf

def calculateMetrics(self, y_test, y_pred):
    metrics = {}
    metrics['accuracy_score'] = accuracy_score(y_test, y_pred)
    metrics['precision_score'] = precision_score(y_test, y_pred, average='weighted')
    metrics['recall_score'] = recall_score(y_test, y_pred, average='weighted')
    metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted')
    num_labels = [float(idx) for idx, label in enumerate(self.labels)]
    target_names = self.labels
    if self.use_unlabelled:
        num_labels.append(float(len(num_labels)))
        target_names.append(self.unlabelled_name)
    metrics['confusion_matrix'] = array2string(confusion_matrix(y_test, y_pred, labels=num_labels))
    metrics['classification_report'] = classification_report(y_test, y_pred, labels=num_labels, zero_division=0, target_names=target_names)
    return metrics


async def train(trainReq, project, background_tasks):
    data = trainReq.dict(by_alias=True)
    storedHyperparameters = [{"name": str(x["name"]), "value": str(x["value"])} for x in trainReq.modelInfo.hyperparameters]
    model = Model(name = trainReq.name, hyperparameters=storedHyperparameters, classifier=trainReq.modelInfo.classifier, labeling=trainReq.labeling, datasets=data["datasets"], projectId=project)
    id = await add_model(model=model.dict(by_alias=True))

    

    await update_model_status(id, project, ModelStatus.preprocessing)
    model = Model(name = trainReq.name, hyperparameters=storedHyperparameters, classifier=trainReq.modelInfo.classifier, labeling=trainReq.labeling, datasets=data["datasets"])
    

    # Get the datasets and lableings used for training
    datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
    labeling = await get_labeling(trainReq.labeling, project)
    
    labelMap = {str(x.id): i+1 for i, x in enumerate(labeling.labels)}
    print(labelMap)

    all_windows = []
    all_labels = []

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

    await update_model_status(id, project, ModelStatus.fitting_model)
    clf = trainClassifier(all_windows, all_labels)

    await update_model_status(id, project, ModelStatus.evaluating)


    return clf, 



    return id


# def extract_features(data: pd.DataFrame):
#     print(data.head())
#     settings = tsfresh.feature_extraction.settings.MinimalFCParameters()
#     data_x = tsfresh.extract_features(
#         data, column_id="time", default_fc_parameters=settings
#     )
#     return data_x

def sliding_windows(data: pd.DataFrame, window_size, stride):
    
    d = data.to_numpy()

    idx = 0
    fused = []
    while idx < d.shape[0]:
        if idx+window_size > d.shape[0]:
            break
        fused.append(d[idx: idx+window_size])
        idx += stride

    labels = []
    windows = []

    for w in fused:
        windows.append(w[:, :-1])
        counts = np.bincount(w[:,2].astype(int))
        label = np.argmax(counts)
        labels.append(label)

    windows = np.array(windows)
    labels = np.array(labels)
    print(windows.shape)
    print(len(label))

def add_labeling(df):
    arr = df.to_numpy()
    n = np.empty((len(df), 1))
    d = np.concatenate([arr, n])



async def getData(datasets, labeling, project):
    labeling = await get_labeling(labeling, project)
    datasets = [await get_dataset(x.id, project) for x in datasets]

    windows = []

    for dataset in datasets:
        df = None
        for ts in dataset.timeSeries:
            binStore =  BinaryStore(ts.id)
            binStore.loadSeries()
            ts_data = binStore.getFull()
            time = ts_data["time"]
            values = ts_data["data"]
            if df is None:
                df = pd.DataFrame({"time": time, ts.id: values})
            else:
                df_new = pd.DataFrame({"time": time, ts.id: values})
                df = pd.merge(df, df_new, on="time", how="outer")
        df = df.interpolate(method='linear')
        arr = add_labeling(df)
        arr = sliding_windows(df, 50, 20)
        extract_features(data= df)



        break



@dataclass
class Trainer:
    name: str
    project_id: str
    target_labeling: Any
    labels: Any
    selected_timeseries: Any
    window_size: Any
    sliding_step: Any
    windowing_mode: str
    use_unlabelled: Any
    unlabelled_name: Any
    selected_model: Any
    validation: ValidationBody
    sub_level: Any = field(default="standard")

    datasets: Any = field(init=False)
    hyperparameters: Any = field(init=False)
    training_state: TrainingState = field(default=None)
    id: str = field(default=None)
    error_msg: str = field(default="")

    def __post_init__(self):
        self.id = uuid.uuid4().hex
        self.training_state = TrainingState.NO_TRAINING_YET

    def _calculate_model_metrics(self, y_test, y_pred):
        metrics = {}
        metrics['accuracy_score'] = accuracy_score(y_test, y_pred)
        metrics['precision_score'] = precision_score(y_test, y_pred, average='weighted')
        metrics['recall_score'] = recall_score(y_test, y_pred, average='weighted')
        metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted')
        num_labels = [float(idx) for idx, label in enumerate(self.labels)]
        target_names = self.labels
        if self.use_unlabelled:
            num_labels.append(float(len(num_labels)))
            target_names.append(self.unlabelled_name)
        metrics['confusion_matrix'] = array2string(confusion_matrix(y_test, y_pred, labels=num_labels))
        metrics['classification_report'] = classification_report(y_test, y_pred, labels=num_labels, zero_division=0, target_names=target_names)
        return metrics

    def feature_extraction(self, df_labeled_each_dataset, dataset_metadatas):
        (df_sliding_window, data_y, metadatas) = roll_sliding_window(df_labeled_each_dataset, self.window_size, self.sliding_step, len(self.selected_timeseries), dataset_metadatas=dataset_metadatas, mode=self.windowing_mode)
        if self.windowing_mode == SAMPLE_BASED_WINDOWING:
            if df_sliding_window.shape[0] // self.window_size <= 1:
                raise ValueError("Not enough features to extract, try setting the window size to a lower value")
        ############# FEATURE_EXTRACTION
        settings = tsfresh.feature_extraction.settings.MinimalFCParameters()
        data_x = tsfresh.extract_features(
            df_sliding_window, column_id="id", default_fc_parameters=settings
        )

        return data_x, data_y, metadatas
    
    def train(self, data_x, data_y, metadatas):
        x_train, x_test, y_train, y_test, metadatas_train, _ = self.validation.train_test_split.train_test_split(data_x, data_y, metadatas)
        ############### MODEL_TRAINING
        scaler = RobustScaler()
        scaler.fit(x_train)
        trans_x_train = scaler.transform(x_train)
        trans_x_test = scaler.transform(x_test)
        trans_x_train = pd.DataFrame(trans_x_train, columns=x_train.columns)
        trans_x_test = pd.DataFrame(trans_x_test, columns=x_test.columns)
        trans_x_train.describe()
        self.selected_model.hyperparameters = self.hyperparameters
        self.selected_model.fit(trans_x_train, y_train)
        y_pred = self.selected_model.predict(trans_x_test)
        print("accuracy_score train :", accuracy_score(y_test, y_pred))
        print('confusion matrix: ', confusion_matrix(y_test, y_pred))
        print('precision', precision_score(y_test, y_pred, average='weighted'))
        print('recall', recall_score(y_test, y_pred, average='weighted'))
        print('f1', f1_score(y_test, y_pred, average='weighted'))

        scaler_serialized = {"scale": list(scaler.scale_), "center": list(scaler.center_), "name": RobustScaler.__name__}

        cross_val_res = [ c_val.cross_validate(self.selected_model, x_train, y_train, metadatas_train) for c_val in self.validation.cross_validation ]
        ############# TRAINING_SUCCESSFUL
        return (self.selected_model, self._calculate_model_metrics(y_test, y_pred), scaler_serialized, cross_val_res)

    
    def get_df_labeled_each_dataset(self):
        ############# TRAINING_INITIATED
        labels_with_intervals = [extract_labels(dataset, self.target_labeling) for dataset in self.datasets]
        # if dataset does not have the target labeling, filter it
        filtered_datasets = [dataset for idx, dataset in enumerate(self.datasets) if labels_with_intervals[idx]]
        labels_with_intervals = list(filter(None, labels_with_intervals))
        if not filtered_datasets:
            raise ValueError("Datasets do not have the target labeling")
        # self.labels is assumed to have no duplicates
        label_map = {label: idx for idx, label in enumerate(self.labels)}
        if self.use_unlabelled:
            label_map[self.unlabelled_name] = len(label_map)
        df_list_each_dataset = [create_dataframes(dataset, self.selected_timeseries) for dataset in filtered_datasets]
        df_merged_each_dataset = [merge_dataframes(df_list) for df_list in df_list_each_dataset]
        df_interpolated_each_dataset = [interpolate_values(df, "linear", "both") for df in df_merged_each_dataset]
        
        return (list(label_map.keys()), [
            label_dataset(df, labels_with_intervals[idx], label_map, self.use_unlabelled, self.unlabelled_name)
            for idx, df in enumerate(df_interpolated_each_dataset)
        ], [ x['metaData'] for x in filtered_datasets ])