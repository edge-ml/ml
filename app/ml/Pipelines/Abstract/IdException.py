class IdException(Exception):
    "Raised when there is an issue with an id of a pipeline step"
    pass
    def __init__(self, name, message=""):
        self.name = name
        self.message = message

        super().__init__(self.name + ": " + self.message)