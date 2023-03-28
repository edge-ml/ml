from bson.codec_options import CodecOptions, TypeEncoder, TypeRegistry, TypeCodec
from app.DataModels.parameter import SelectionParameter, NumberParameter
from pydantic import BaseModel
from typing import Dict



def encode_pydantic(value):
    return value.dict(by_alias=True)

class SelectionParamterEncoder(TypeCodec):
    python_type = SelectionParameter
    bson_type = Dict

    def transform_python(self, value):
        return value.dict(by_alias=True)

    def transform_bson(self, value):
        return SelectionParameter.parse_obj(value)

class NumberParameterEncoder(TypeCodec):
    python_type = NumberParameter
    bson_type = Dict

    def transform_python(self, value):
        return value.dict(by_alias=True)

    def transform_bson(self, value):
        return NumberParameter.parse_obj(value)

registry = TypeRegistry([SelectionParamterEncoder(), NumberParameterEncoder()])

codec_options = CodecOptions(type_registry=registry)