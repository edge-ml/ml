

class AbstractPipeLineCreator():

    @classmethod
    def get_name(cls):
        raise NotImplementedError()
    
    @classmethod
    def get_description(cls):
        raise NotImplementedError()
    
    @classmethod
    def get_categories(cls):
        raise NotImplementedError()

    @classmethod
    def get_train_config(cls):
        return {"name": cls.get_name(), "description": cls.get_description(), "steps": [x.get_train_config() for x in cls.get_categories()]}