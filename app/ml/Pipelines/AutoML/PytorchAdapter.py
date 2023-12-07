import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


class CustomDataset(Dataset):
    def __init__(self, data, labels):
        assert len(data) == len(labels)
        data = np.float32(data)
        self.data = torch.tensor(data, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return (self.data[index], self.labels[index])
    
def get_dataloader(data_array, label_array):
    custom_dataset = CustomDataset(data_array, label_array)
    dataloader = DataLoader(custom_dataset, 8, shuffle=True)
    return dataloader
    

