

class BaseStorageProvider():

    @classmethod
    def save(self, id, data):
        raise NotImplementedError()

    @classmethod
    def load(self, id):
        raise NotImplementedError()
    
    @classmethod
    def delete(self, id):
        raise NotImplementedError()