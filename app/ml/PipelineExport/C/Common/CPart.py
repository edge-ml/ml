from app.ml.PipelineExport.C.Common.Memory import Memory

from typing import List

from jinja2 import Template

from typing import Dict

class CStep():
    def __init__(self, variables, code, input_shape: List[int], output_shape: List[int], globals=[], includes=[]) -> None:
        self.variables : Dict = variables
        self.code : str = code
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.globals : List[str] = globals
        self.includes : List[str] = includes
        
    def compile(self, name):
        template = Template(self.code)
        rendered_code = template.render({**self.variables, "name": name, "input_shape": self.input_shape, "output_shape": self.output_shape})
        return rendered_code