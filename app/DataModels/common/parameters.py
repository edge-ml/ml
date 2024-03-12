from pydantic import BaseModel, RootModel, Field
from typing import Union, List, Literal
from typing_extensions import TypeAliasType, Annotated

Number = Union[float, int]

class NumberParameter(BaseModel):
    name: str
    parameter_type: Literal["number"]
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
    parameter_type: Literal["selection"]
    display_name: str
    parameter_name: str
    description: str
    options: List[str]
    value: Union[str, None]
    multi_select: bool
    required: bool
    is_advanced: bool

class TextParameter(BaseModel):
    name: str
    parameter_type: Literal["text"]
    display_name: str
    parameter_name: str
    description: str
    value: Union[str, None]
    required: bool
    is_advanced: bool


# class Parameter(RootModel):
#     root: Union[NumberParameter, SelectionParameter, TextParameter] = Field(..., discriminator="parameter_type")

Parameter = TypeAliasType("Parameter", Annotated[Union[NumberParameter, TextParameter, SelectionParameter], Field(discriminator="parameter_type")])
