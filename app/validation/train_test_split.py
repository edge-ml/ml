from .base_validation import BaseTrainTestSplit
from pydantic import validator
from typing import List, Any, Union
from sklearn.model_selection import train_test_split as sklearn_train_test_split

class TrainTestSplit(BaseTrainTestSplit):
    _name = 'Train Test Split'

    test_size: float
    @validator('test_size')
    def test_size_must_be_between_0_1(cls, v):
        if v > 1.0 or v < 0:
            raise ValueError('test size must be between 0 and 1')
        return v

    def train_test_split(self, *arrays: any) -> List[Union[List, Any]]:
        return sklearn_train_test_split(
            *arrays, random_state=5, test_size=self.test_size
        )