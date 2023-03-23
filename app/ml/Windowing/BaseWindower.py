

class BasicWindower():

    def __init__(self, hyperparameters=[]):
        self._hyperparameters = hyperparameters

    @staticmethod
    def get_name():
        raise NotImplementedError()

    @staticmethod
    def get_config():
        raise NotImplementedError()

    @staticmethod
    def get_platforms():
        raise NotImplementedError()

    @staticmethod
    def get_description():
        raise NotImplementedError()

    @staticmethod
    def config():
        raise NotImplementedError()

    @staticmethod
    def get_Hyperparameters():
        raise NotImplementedError()

    def window(self, datasets):
        raise NotImplementedError()

    @property
    def hyperparameters(self):
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, value):
        self._hyperparameters = value
        params = {x["name"]: x["value"] for x in self._hyperparameters}
        self.clf.set_params(**params)