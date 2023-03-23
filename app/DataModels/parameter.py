from pydantic import BaseModel
from typing import Union, List

Number = Union[int, float]

class NumberParameter(BaseModel):
    name: str
    display_name: str
    parameter_name: str
    description: str
    number_min: Number
    number_max: Number
    value: Union[Number, None]
    step_size: Number
    required: bool
    log: bool
    is_advanced: bool


class SelectionParameter(BaseModel):
    name: str
    display_name: str
    parameter_name: str
    description: str
    options: List[str]
    value: Union[str, None]
    multi_select: bool
    required: bool
    is_advanced: bool


Parameter = Union[NumberParameter, SelectionParameter]
