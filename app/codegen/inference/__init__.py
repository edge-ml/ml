from typing import List

from codegen.inference.BasePlatform import BasePlatform
from codegen.inference.CPlatform import CPlatform
from codegen.inference.JavascriptPlatform import JavascriptPlatform
from codegen.inference.PythonPlatform import PythonPlatform
from codegen.inference.ArduinoPlatform import ArduinoPlatform

platforms: List[BasePlatform] = [
    CPlatform(),
    JavascriptPlatform(),
    PythonPlatform(),
    ArduinoPlatform()
]