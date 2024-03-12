from ml.PipelineExport.C.Common.Memory import Memory

from typing import List

from jinja2 import Template, FileSystemLoader, Environment

from typing import Dict

templateLoader = FileSystemLoader(searchpath="app/ml/PipelineExport/C")
templateEnv = Environment(loader=templateLoader)

class ExtraFile():
    def __init__(self, name, content) -> None:
        self.content = content
        self.name = name

class CStep():
    def __init__(self, variables, code, input_shape: List[int], output_shape: List[int], globals=[], includes=[], extra_files : List[ExtraFile] = []) -> None:
        self.variables : Dict = variables
        self.code : str = code
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.globals : List[str] = globals
        self.includes : List[str] = includes
        self.extra_files: List[ExtraFile] = extra_files
        
    def compile(self, name, args={}):
        template = templateEnv.from_string(self.code)
        rendered_code = template.render({**self.variables, **args, "name": name, "input_shape": self.input_shape, "output_shape": self.output_shape})
        return rendered_code