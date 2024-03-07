from pydantic import BaseModel, Field
from typing import Union, List, Literal, Annotated

Number = Union[float, int]

class NumberParameter(BaseModel):
    name: str
    parameter_type: Literal["number"]
    display_name: str
    parameter_name: str
    description: str
    number_min: Number
    number_max: Number
    value: Number = None
    step_size: Number
    required: bool
    log: bool
    is_advanced: bool

class SelectionParameter(BaseModel):
    name: str
    parameter_type: Literal["selection"]
    display_name: str
    parameter_name: str
    description: str
    options: List[str]
    value: str = None
    multi_select: bool
    required: bool
    is_advanced: bool

class TextParameter(BaseModel):
    name: str
    parameter_type: Literal["text"]
    display_name: str
    parameter_name: str
    description: str
    value: str = None
    required: bool
    is_advanced: bool

Parameter = Annotated[Union[NumberParameter, SelectionParameter, TextParameter], Field(discriminator="parameter_type")]
