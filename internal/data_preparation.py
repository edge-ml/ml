import pandas as pd

def extract_labels(dataset, selected_labeling_id):
    labeling = next((l for l in dataset['labelings'] if l['labelingId'] == selected_labeling_id), None)
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