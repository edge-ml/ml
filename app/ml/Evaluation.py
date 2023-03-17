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

from app.validation import ValidationBody
from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset
from time import sleep

from sklearn.tree import DecisionTreeClassifier
from app.models.decision_tree import DecisionTree
from app.models.decision_tree import DecisionTree
from app.models.random_forest import RandomForest


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