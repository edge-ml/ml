from typing import List

from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.CPlatform import CPlatform
from app.codegen.inference.JavascriptPlatform import JavascriptPlatform
from app.codegen.inference.PythonPlatform import PythonPlatform

platforms: List[BasePlatform] = [
    CPlatform(),
    JavascriptPlatform(),
    PythonPlatform(),
]