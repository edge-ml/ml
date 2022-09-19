from enum import Enum
from pydantic import BaseModel
from typing import List, Any, Union

class Type(Enum):
    TrainTestSplit = 'TrainTestSplit'
    CrossValidation = 'CrossValidation'

class BaseValidation(BaseModel):
    type: Type

class BaseTrainTestSplit(BaseModel):
    type = Type.TrainTestSplit

    def train_test_split(self, *arrays: any) -> List[Union[List, Any]]:
        raise NotImplementedError("Not implemented")

class BaseCrossValidation(BaseModel):
    type = Type.CrossValidation

    def cross_validate(self, model, data, target, metadatas):
        raise NotImplementedError("Not implemented")