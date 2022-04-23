from asyncio import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor
from typing import Any
import uuid

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

from app.internal.data_preparation import (
    extract_labels,
    create_dataframes,
    interpolate_values,
    label_dataset,
    merge_dataframes,
    roll_sliding_window,
)

from app.ml.training_state import TrainingState

class Trainer:
    training_state: TrainingState = TrainingState.NO_TRAINING_YET
    id: str

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
            target_names.append("Other")
        metrics['confusion_matrix'] = array2string(confusion_matrix(y_test, y_pred, labels=num_labels))
        metrics['classification_report'] = classification_report(y_test, y_pred, labels=num_labels, zero_division=0, target_names=target_names)
        return metrics

    def __init__(
        self,
        name, project_id, target_labeling, labels, datasets, selected_timeseries,
        window_size, sliding_step, use_unlabelled,
        selected_model, hyperparameters
    ) -> None:
        self.id = uuid.uuid4().hex
        self.name = name
        self.project_id = project_id
        self.target_labeling = target_labeling
        self.labels = labels
        self.datasets = datasets
        self.selected_timeseries = selected_timeseries
        self.window_size = window_size
        self.sliding_step = sliding_step
        self.use_unlabelled = use_unlabelled
        self.selected_model = selected_model
        self.hyperparameters = hyperparameters

        print("trainer created")

    def _setTrainingState(self, t: TrainingState):
        self.training_state = t

    def feature_extraction(self, df_labeled_each_dataset):
        (df_sliding_window, data_y) = roll_sliding_window(df_labeled_each_dataset, self.window_size, self.sliding_step, len(self.selected_timeseries))
        if df_sliding_window.shape[0] // self.window_size <= 1:
            raise ValueError("Not enough features to extract, try setting the window size to a lower value")
        ############# FEATURE_EXTRACTION
        self._setTrainingState(TrainingState.FEATURE_EXTRACTION)
        settings = tsfresh.feature_extraction.settings.MinimalFCParameters()
        data_x = tsfresh.extract_features(
            df_sliding_window, column_id="id", default_fc_parameters=settings
        )

        return data_x, data_y
    
    def train(self, data_x, data_y):
        x_train, x_test, y_train, y_test = train_test_split(
            data_x, data_y, random_state=5, test_size=0.33
        )  # TODO fix hardcoded
        ############### MODEL_TRAINING
        self._setTrainingState(TrainingState.MODEL_TRAINING)
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
        ############# TRAINING_SUCCESSFUL
        self._setTrainingState(TrainingState.TRAINING_SUCCESSFUL)
        return (self.selected_model, self._calculate_model_metrics(y_test, y_pred))

    
    def get_df_labeled_each_dataset(self):
        ############# TRAINING_INITIATED
        self._setTrainingState(TrainingState.TRAINING_INITIATED)
        labels_with_intervals = [extract_labels(dataset, self.target_labeling) for dataset in self.datasets]
        # if dataset does not have the target labeling, filter it
        filtered_datasets = [dataset for idx, dataset in enumerate(self.datasets) if labels_with_intervals[idx]]
        # self.labels is assumed to have no duplicates
        label_map = {label: idx for idx, label in enumerate(self.labels)}
        if self.use_unlabelled:
            label_map["Other"] = len(label_map)
        df_list_each_dataset = [create_dataframes(dataset, self.selected_timeseries) for dataset in filtered_datasets]
        df_merged_each_dataset = [merge_dataframes(df_list) for df_list in df_list_each_dataset]
        df_interpolated_each_dataset = [interpolate_values(df, "linear", "both") for df in df_merged_each_dataset]
        
        return (list(label_map.keys()), [
            label_dataset(df, labels_with_intervals[idx], label_map, self.use_unlabelled)
            for idx, df in enumerate(df_interpolated_each_dataset)
        ])