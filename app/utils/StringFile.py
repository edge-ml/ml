
class StringFile():
    def __init__(self, content, name) -> None:
        self.content = content
        self.name = name 
        
    def read(self):
        return self.content