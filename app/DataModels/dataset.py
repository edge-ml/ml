from pydantic import BaseModel
from bson.objectid import ObjectId
from app.utils.PyObjectId import PyObjectId
from pydantic import Field
from typing import Any, Optional, List, Dict

class SamplingRateSchema(BaseModel):
    mean: float
    var: float

class TimeSeries(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    start: int
    end: int
    unit: str = Field(default="")
    # Physical quantity (catalog id, custom label, or None when unknown).
    quantity: Optional[str] = None
    name: str
    data: List | None = None
    samplingRate: SamplingRateSchema

class DatasetLabels(BaseModel):
    start: int
    end: int
    type: PyObjectId
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")

class DatasetLabeling(BaseModel):
    labelingId: PyObjectId
    labels: List[DatasetLabels]

class MediaSeries(BaseModel):
    """An audio or video recording of a dataset (stored by the dataset-store
    under media/{id}). start is where it begins on the dataset timeline."""
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    kind: str
    name: str
    start: int
    end: int
    durationMs: int
    status: Optional[str] = None
    startSource: Optional[str] = None
    meta: Dict[str, Any] = Field(default={})

    @property
    def has_sound(self) -> bool:
        return self.kind == "audio" or bool((self.meta or {}).get("audioCodec"))


class DatasetSchema(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    projectId: PyObjectId = Field(default_factory=ObjectId)
    name: str
    metaData: Dict[str, str] = Field(default={})
    timeSeries: List[TimeSeries]
    labelings: List[DatasetLabeling] = Field(default=[])
    # audio and video recordings; only the audio pipeline reads them
    mediaSeries: List[MediaSeries] = Field(default=[])