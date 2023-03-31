from typing import List, Dict

class CPart():

    def __init__(self, includes : List, globals : List, code : str, jinjaVars : Dict) -> None:
        self.includes = includes
        self.globals = globals
        self.code = code
        self.jinjaVars = jinjaVars