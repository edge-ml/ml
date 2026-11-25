"""Inputs of the audio pipeline (#100): per dataset, the selected sensor
channels (each on its own timestamps), the selected recording with sound, and
the labels as time intervals. Nothing is merged or resampled here; the
time-based windower does that per window."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.DataModels.dataset import DatasetSchema, MediaSeries


@dataclass
class LabelIntervals:
    starts: np.ndarray  # ms
    ends: np.ndarray  # ms, inclusive like everywhere in edge-ml
    classes: np.ndarray  # class index per interval


@dataclass
class RecordingSource:
    dataset_id: str
    meta: Dict
    sensor_names: List[str]
    sensor_ids: List[str]
    sensor_spans: List[Tuple[float, float]]
    sensor_periods_ms: List[float]
    conversions: Dict[str, Tuple[float, float]]
    audio: Optional[MediaSeries]
    labels: LabelIntervals
    zero_class: Optional[int] = None
    _sensors: Optional[List[Tuple[np.ndarray, np.ndarray]]] = field(default=None, repr=False)

    def span(self) -> Optional[Tuple[float, float]]:
        """The time covered by every selected input, or None."""
        spans = list(self.sensor_spans)
        if self.audio is not None:
            spans.append((float(self.audio.start), float(self.audio.start + self.audio.durationMs)))
        if not spans:
            return None
        start = max(s for s, _ in spans)
        end = min(e for _, e in spans)
        return (start, end) if end > start else None

    def load_sensors(self):
        """[(time_ms float64, values float32)] per selected channel, in the
        units the model expects."""
        if self._sensors is None:
            from app.DataProcessor.DataLoader.binaryStore import BinaryStore

            loaded = []
            for ts_id in self.sensor_ids:
                store = BinaryStore(ts_id)
                store.loadSeries()
                values = np.asarray(store.data_arr, dtype=np.float64)
                if ts_id in self.conversions:
                    scale, offset = self.conversions[ts_id]
                    values = values * scale + offset
                times = np.asarray(store.time_arr, dtype=np.float64)
                order = np.argsort(times, kind="stable")
                loaded.append((times[order], values[order].astype(np.float32)))
            self._sensors = loaded
        return self._sensors


def build_sources(datasets: List[DatasetSchema], reqLabeling, labelMap, conversions=None) -> List[RecordingSource]:
    """datasets must already be filtered to the selected timeSeries and
    mediaSeries (see trainer.init_train)."""
    conversions = conversions or {}
    zero = labelMap.get("Zero") if reqLabeling.useZeroClass else None
    sources = []
    for ds in datasets:
        labeling = next((l for l in ds.labelings if l.labelingId == reqLabeling.id), None)
        intervals = [] if labeling is None else [
            l for l in labeling.labels if l.type not in reqLabeling.disabledLabelIDs and str(l.type) in labelMap
        ]
        labels = LabelIntervals(
            starts=np.array([float(l.start) for l in intervals], dtype=np.float64),
            ends=np.array([float(l.end) for l in intervals], dtype=np.float64),
            classes=np.array([labelMap[str(l.type)] for l in intervals], dtype=np.int64),
        )
        audio = next((m for m in ds.mediaSeries if m.has_sound), None)
        sources.append(RecordingSource(
            dataset_id=str(ds.id),
            meta=ds.metaData,
            sensor_names=[ts.name for ts in ds.timeSeries],
            sensor_ids=[str(ts.id) for ts in ds.timeSeries],
            sensor_spans=[(float(ts.start), float(ts.end)) for ts in ds.timeSeries],
            sensor_periods_ms=[float(ts.samplingRate.mean) for ts in ds.timeSeries],
            conversions={
                str(ts_id): value for (ds_id, ts_id), value in conversions.items() if ds_id == str(ds.id)
            },
            audio=audio,
            labels=labels,
            zero_class=zero,
        ))
    return sources


class RecordingsError(ValueError):
    pass


def align_sources(sources: List[RecordingSource]) -> List[RecordingSource]:
    """Every dataset must give the model the same inputs: the same sensor
    channels (put into the first dataset's order here) and, for all or none of
    them, a recording with sound."""
    if not sources:
        raise RecordingsError("Select at least one dataset.")
    names = sources[0].sensor_names
    with_audio = [s for s in sources if s.audio is not None]
    if with_audio and len(with_audio) != len(sources):
        raise RecordingsError(
            f"{len(sources) - len(with_audio)} of {len(sources)} selected datasets have no selected recording with sound. "
            "Select a recording in every dataset, or none.")
    for s in sources[1:]:
        if sorted(s.sensor_names) != sorted(names):
            raise RecordingsError("The selected datasets have different sensors: "
                                  f"{', '.join(names) or 'none'} vs {', '.join(s.sensor_names) or 'none'}.")
        order = [s.sensor_names.index(n) for n in names]
        for attr in ("sensor_names", "sensor_ids", "sensor_spans", "sensor_periods_ms"):
            values = getattr(s, attr)
            setattr(s, attr, [values[i] for i in order])
    return sources
