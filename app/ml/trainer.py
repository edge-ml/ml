from typing import Any
import uuid

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