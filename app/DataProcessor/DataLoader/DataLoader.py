import numpy as np
import pandas as pd
import math


from app.DataProcessor.DataLoader.binaryStore import BinaryStore


def processDatasets(datasets, labeling_id, labelMap, useZero):
    

    samplingRate = min([ts.samplingRate.mean for d in datasets for ts in d.timeSeries])
    
    
    res = []
    for dataset in datasets:
        # Get labels in datasets
        print("labels", "-"*20)
        print([x.labelingId for x in dataset.labelings], labeling_id)
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

        maxVal = max(labelMap.values())

        for i, t in enumerate(arr):
            for l in labels:
                if t[0] >= int(l.start) and t[0] <= int(l.end):
                    arr[i][-1] = labelMap[str(l.type)]
                    break
                else:
                    arr[i][-1] = maxVal if useZero else 9*10^10 
        res.append(arr)
    return res, samplingRate