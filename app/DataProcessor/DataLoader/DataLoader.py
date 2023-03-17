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
from app.DataProcessor.DataLoader.binaryStore import BinaryStore
from time import sleep

from sklearn.tree import DecisionTreeClassifier
from app.models.decision_tree import DecisionTree
from app.models.decision_tree import DecisionTree
from app.models.random_forest import RandomForest

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