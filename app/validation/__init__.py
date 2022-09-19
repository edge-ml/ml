from pydantic import BaseModel, Field
from typing import List, Optional, Union
from typing_extensions import Annotated

from .leave_one_subject_out import LeaveOneSubjectOut
from .train_test_split import TrainTestSplit

# CrossValidation = Annotated[
#     Union[LeaveOneSubjectOut],
#     Field(discriminator="type")
# ]
CrossValidation = LeaveOneSubjectOut

class ValidationBody(BaseModel):
    train_test_split: TrainTestSplit
    cross_validation: Optional[List[CrossValidation]] = []

VALIDATION_TEST_METHODS = [
    LeaveOneSubjectOut._name,
    TrainTestSplit._name,
]