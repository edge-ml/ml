from app.DataModels.parameter import Parameter

class BaseConfig():

    def __init__(self, parameters : Parameter = []):
        self.parameters = parameters

    @staticmethod
    def get_name():
        raise NotImplementedError()

    @staticmethod
    def get_desciption():
        raise NotImplementedError()

    @staticmethod
    def get_platforms():
        return []

    # Hyperparameters that can be set for the config
    @staticmethod
    def get_parameters():
        return []


    def get_state(self):
        return {"name": self.get_name(), "description": self.get_desciption(), "config": self.get_config()}
    
    def persist(self):
        return {"name": self.get_name(), "parameters": self.parameters}

    @classmethod
    def get_train_config(cls):
        print(cls.get_name())
        return {
        "name": cls.get_name(),
        "description":  cls.get_description(),
        "parameters":  cls.get_parameters(),
        "platforms":  cls.get_platforms()
        }

    def get_param_value_by_name(self, name):
        print(self.parameters)
        for param in self.parameters:
            if param.parameter_name == name:
                return param.value
        raise KeyError(f"Parameter with name {name} not found")
        