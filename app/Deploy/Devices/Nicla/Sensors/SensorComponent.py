
class SensorComponent:
    
    def __init__(self, name : str, dtype: str) -> None:
        self.name = name
        self.dtype = dtype

    def get_config(self):
        return {"name": self.name, "dtype": self.dtype}