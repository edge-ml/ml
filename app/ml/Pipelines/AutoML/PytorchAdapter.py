import torch
from torch.utils.data import Dataset, Dataloader


class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = torch.tensor(data, dtype=torch.float32)

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data[index]
    
def get_dataloader(data_array):
    custom_dataset = CustomDataset(data_array)
    dataloader = Dataloader(custom_dataset, 32, shuffle=True)
    return dataloader
    

