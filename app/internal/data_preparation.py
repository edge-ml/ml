import numpy as np
import pandas as pd

def filter_by_timeseries(datasets, timeseries):
    filtered_dataset = []
    for dataset in datasets:
        dataset_series = [t['name'] for t in dataset['timeSeries']]
        valid = True
        for t in timeseries:
            if t not in dataset_series:
                valid = False
                break
        if valid:
            filtered_dataset.append(dataset)
    return filtered_dataset

def extract_labels(dataset, target_labeling):
    labeling = next(
        (l for l in dataset["labelings"] if l["labelingId"] == target_labeling), None
    )
    if not labeling:
        return []
    labels = [
        {"start": l["start"], "end": l["end"], "label_id": l["type"]}
        for l in labeling["labels"]
    ]
    return labels


def create_dataframes(dataset, selected_timeseries):
    timeseries = [t for t in dataset["timeSeries"] if t["name"] in selected_timeseries]
    df_list = []
    
    for t in timeseries:
        sensor = t["name"]
        timestamps = []
        datapoints = []
        for d in t["data"]:
            timestamp = d["timestamp"]
            datapoint = d["datapoint"]
            timestamps.append(timestamp)
            datapoints.append(datapoint)
        
        df = pd.DataFrame()
        df[sensor] = datapoints
        df.index = timestamps
        df.index = pd.to_datetime(df.index, unit="ms")
        df_list.append(df)

    return df_list


def merge_dataframes(dataframes):
    merged = dataframes[0]
    for i in range(1, len(dataframes)):
        merged = pd.merge(
            merged, dataframes[i], left_index=True, right_index=True, how="outer"
        )
    return merged


def concat_dataframes(dataframes):
    return pd.concat(dataframes)


def interpolate_values(df, method, direction):
    return df.interpolate(method=method, limit_direction=direction)


def label_dataset(df, labels, label_map, use_unlabelled, unlabelled_name):
    label_list = np.array([np.NAN] * df.shape[0])
    df_labeled = df.copy()
    df_labeled_temp = df_labeled.reset_index()
    for interval in labels:
        label = interval["label_id"]
        start = pd.to_datetime(interval["start"], unit="ms")
        end = pd.to_datetime(interval["end"], unit="ms")
        df_interval = df_labeled_temp[
            (df_labeled_temp["index"] >= start) & (df_labeled_temp["index"] <= end)
        ]
        label_list[df_interval.index] = label_map[label]
    df_labeled["labels"] = label_list
    if use_unlabelled:
        df_labeled["labels"] = df_labeled["labels"].fillna(label_map[unlabelled_name])
    return df_labeled


def roll_sliding_window(df_labeled_each_dataset, window_size, step_size, col_size):
    id = 0
    data_y = []
    df_sliding_window = pd.DataFrame()
    for df in df_labeled_each_dataset:
        for i in range(0, df.shape[0], step_size):
            window_start = i
            window_end = i + window_size
            if window_end > df.shape[0]:
                break
            most_voted = df.iloc[window_start:window_end, col_size].mode()
            if most_voted.empty:
                continue
            df_segment = df.iloc[window_start:window_end, :col_size]
            df_segment["id"] = id
            id = id + 1
            df_sliding_window = pd.concat([df_sliding_window, df_segment])
            data_y.append(most_voted.iloc[0])
    print(data_y)
    return (df_sliding_window, data_y)


# TODO handle multiple choice
def format_hyperparameters(hyperparameters):
    formatted = {}
    for param in hyperparameters:
        param_name = param["parameter_name"]
        if param_name == "window_size" or param_name == "sliding_step":
            continue
        param_value = (
            param["state"]["value"]
            if isinstance(param["state"], dict)
            else param["state"]
        )
        if param_value == "True":
            param_value = True
        elif param_value == "False":
            param_value = False
        formatted[param_name] = param_value
    return formatted
