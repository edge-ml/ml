import numpy as np
import pandas as pd

def extract_labels(dataset, target_labeling):
    labeling = next((l for l in dataset['labelings'] if l['labelingId'] == target_labeling), None)
    if not labeling:
        raise "Dataset is not labeled with target labeling"
    # print(labeling['labels'])
    labels = [{'start': l['start'], 'end': l['end'], 'label_id':l['type']} for l in labeling['labels']]
    return labels

def create_dataframes(dataset, selected_timeseries):
    timeseries = [t for t in dataset['timeSeries'] if t['name'] in selected_timeseries]
    df_list = []
    for t in timeseries:
        sensor = t['name']
        timestamps = []
        datapoints = []
        for d in t['data']:
            timestamp = d['timestamp']
            datapoint = d['datapoint']
            timestamps.append(timestamp)
            datapoints.append(datapoint)
        df = pd.DataFrame()
        df[sensor] = datapoints
        df.index = timestamps
        df.index = pd.to_datetime(df.index, unit='ms')
        # print(df)
        df_list.append(df)
    return df_list

def merge_dataframes(dataframes):
    merged = dataframes[0]
    for i in range(1, len(dataframes)):
        merged = pd.merge(merged, dataframes[i], left_index=True, right_index=True, how='outer')
    # print(merged)
    return merged

def concat_dataframes(dataframes):
    return pd.concat(dataframes)

def interpolate_values(df, method, direction):
    return df.interpolate(method=method, limit_direction=direction)

def label_dataset(df, labels, label_map):
    label_list = np.array([np.NAN] * df.shape[0])
    df_labeled = df.copy()
    df_labeled_temp = df_labeled.reset_index()
    for interval in labels:
        label = interval['label_id']
        start = pd.to_datetime(interval['start'], unit='ms')
        end  = pd.to_datetime(interval['end'], unit='ms')
        df_interval = df_labeled_temp[(df_labeled_temp['index'] >= start) & (df_labeled_temp['index'] <= end)]
        label_list[df_interval.index]=label_map[label]
    df_labeled['labels'] = label_list
    df_labeled['labels'] = df_labeled['labels'].fillna(label_map['Other'])
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
            df_segment = df.iloc[window_start : window_end, : col_size]
            print(df_segment)
            df_segment['id'] = id
            id = id + 1
            df_sliding_window = pd.concat([df_sliding_window, df_segment])
            data_y.append(df.iloc[window_start : window_end, col_size].mode().iloc[0])
    print(data_y)
    return (df_sliding_window, data_y)    