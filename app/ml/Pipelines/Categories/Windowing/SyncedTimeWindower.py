"""Time-based windowing for the audio pipeline (#100).

Each window covers `window_ms` of the dataset timeline and holds
- the selected sensor channels, linearly interpolated onto a fixed grid of
  `sensor_rate_hz` (so devices that sample unevenly still give the same input
  shape), and
- the audio of the selected recording at `audio_rate_hz`.

The windower outputs one row per window: [windower key, dataset index, first
audio sample, sensor values flattened as (grid, channel)]. The audio itself is
not copied into the rows (a 1 s window at 16 kHz is 16 000 values). The
evaluators split and rebuild the containers after windowing, so the feature
extractor finds this windower, and with it the audio, by the key in the rows
(see `windower_for`); `release` drops the audio after training.

A window's label is the label covering most of its time, by the same rule as
the sample windower (window_majority_label): unlabeled time beats a label only
when it covers more; with the zero class, unlabeled time is the zero class.
"""
import itertools
import threading
from typing import List, Optional

import numpy as np

from app.internal.config import AUDIO_MAX_TOTAL_SECONDS, MAX_TRAIN_WINDOWS
from app.ml.BaseConfig import Platforms
from app.ml.Pipelines.Categories.Windowing.BaseWindower import BaseWindower
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.utils.labels import UNLABELED_LABEL
from app.utils.parameter_builder import ParameterBuilder

AUDIO_RATES = ["16000", "8000"]
# columns before the sensor values in a row: key, dataset index, first audio sample
HEADER = 3
# labels are assigned in chunks so the windows x labels matrix stays small
_LABEL_CHUNK = 4096


class WindowingError(Exception):
    pass


# windowers holding decoded audio, by the key written into their rows
_ACTIVE = {}
_KEYS = itertools.count(1)
_ACTIVE_LOCK = threading.Lock()


def windower_for(rows) -> "SyncedTimeWindower":
    rows = np.asarray(rows)
    key = int(rows[0, 0]) if len(rows) else None
    with _ACTIVE_LOCK:
        windower = _ACTIVE.get(key)
    if windower is None:
        raise WindowingError("The recordings of these windows are no longer loaded.")
    return windower


def window_labels(starts, window_ms, labels, zero_class=None):
    """Label per window starting at `starts` (ms), from label intervals.
    Returns UNLABELED_LABEL for windows to drop."""
    starts = np.asarray(starts, dtype=np.float64)
    out = np.full(len(starts), UNLABELED_LABEL, dtype=np.int64)
    if len(starts) == 0:
        return out
    n_classes = int(max([labels.classes.max() + 1 if len(labels.classes) else 0,
                         (zero_class + 1) if zero_class is not None else 0, 1]))
    for c0 in range(0, len(starts), _LABEL_CHUNK):
        t = starts[c0:c0 + _LABEL_CHUNK, None]
        if len(labels.starts):
            # label ends are inclusive ms, like the sample windower's check
            overlap = np.clip(np.minimum(labels.ends[None, :] + 1, t + window_ms) - np.maximum(labels.starts[None, :], t), 0, None)
            per_class = np.zeros((overlap.shape[0], n_classes))
            for c in np.unique(labels.classes):
                per_class[:, c] = overlap[:, labels.classes == c].sum(axis=1)
        else:
            per_class = np.zeros((t.shape[0], n_classes))
        unlabeled = np.clip(window_ms - per_class.sum(axis=1), 0, None)
        if zero_class is not None:
            per_class[:, zero_class] += unlabeled
            chunk = np.argmax(per_class, axis=1)  # ties go to the lower index, like bincount
            chunk[per_class.max(axis=1) <= 0] = UNLABELED_LABEL
        else:
            top = np.argmax(per_class, axis=1)
            best = per_class[np.arange(len(top)), top]
            chunk = np.where((best > 0) & (best >= unlabeled), top, UNLABELED_LABEL)
        out[c0:c0 + _LABEL_CHUNK] = chunk
    return out


class SyncedTimeWindower(BaseWindower):

    # the trainer hands this windower the recordings (sensors + audio + label
    # intervals) instead of the merged sample array of processDatasets
    consumes_recordings = True

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.sensor_rate = None
        self.audio_rate = None
        self.window_ms = None
        self.stride_ms = None
        self.sensor_samples = 0
        self.audio_samples = 0
        self.channels: List[str] = []
        self.audio_name: Optional[str] = None
        # decoded audio per dataset index, only while training
        self._audio = {}
        self.key = None

    @staticmethod
    def get_name():
        return "Time based (sensors & audio)"

    @staticmethod
    def get_description():
        return ("Cuts the recordings into windows of a fixed duration. Each window holds the selected sensors, "
                "resampled to one rate, and the sound of the selected recording.")

    @staticmethod
    def get_platforms():
        return [Platforms.EXECUTORCH]

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number("window_ms", "Window length (ms)", "Duration of one window.", 100, 10000, 1000, 10, True, False, False)
        pb.add_number("stride_ms", "Window step (ms)", "How far the next window starts after the previous one. Less than the window length makes windows overlap.",
                      10, 10000, 500, 10, True, False, False)
        pb.add_selection("audio_rate_hz", "Audio sample rate (Hz)", "Sound is converted to mono at this rate. 16 kHz keeps speech and most everyday sounds.",
                         AUDIO_RATES, "16000", required=True, is_advanced=True)
        pb.add_number("sensor_rate_hz", "Sensor rate (Hz)", "Sensor values are interpolated onto this rate. 0 uses the lowest rate of the selected sensors.",
                      0, 1000, 0, 1, True, False, True)
        return pb.parameters

    # -- parameters --------------------------------------------------------
    def _param(self, name, default, cast=float):
        try:
            value = self.get_param_value_by_name(name)
        except KeyError:
            return default
        if value is None or value == "":
            return default
        return cast(float(value))

    def _configure(self, sources):
        """Rates and window sizes, from the parameters and the data."""
        self.window_ms = self._param("window_ms", 1000.0)
        self.stride_ms = self._param("stride_ms", 500.0)
        if self.window_ms <= 0 or self.stride_ms <= 0:
            raise WindowingError("Window length and step must be positive.")
        first = sources[0]
        self.channels = list(first.sensor_names)
        self.audio_name = first.audio.name if first.audio is not None else None
        self.audio_rate = self._param("audio_rate_hz", 16000, int) if self.audio_name is not None else None
        rate = self._param("sensor_rate_hz", 0.0)
        if self.channels and rate <= 0:
            periods = [p for s in sources for p in s.sensor_periods_ms if p and p > 0]
            rate = round(1000.0 / max(periods), 2) if periods else 50.0
        self.sensor_rate = float(rate) if self.channels else None
        self.sensor_samples = max(1, int(round(self.window_ms * self.sensor_rate / 1000.0))) if self.channels else 0
        self.audio_samples = int(round(self.window_ms * self.audio_rate / 1000.0)) if self.audio_rate else 0
        if not self.channels and not self.audio_rate:
            raise WindowingError("Select at least one sensor or a recording with sound.")

    # -- planning (no data loaded) -----------------------------------------
    def plan(self, sources):
        """Window starts (ms) and labels per dataset, from the recordings'
        metadata only. Used by the preflight and as the first training step."""
        if self.window_ms is None:
            self._configure(sources)
        plans = []
        for source in sources:
            span = source.span()
            if span is None:
                plans.append((np.zeros(0), np.zeros(0, dtype=np.int64)))
                continue
            first, last = span
            count = int(np.floor((last - first - self.window_ms) / self.stride_ms)) + 1
            starts = first + np.arange(max(count, 0)) * self.stride_ms
            labels = window_labels(starts, self.window_ms, source.labels, source.zero_class)
            keep = labels != UNLABELED_LABEL
            plans.append((starts[keep], labels[keep]))
        return plans

    def audio_seconds(self, sources):
        return sum(s.audio.durationMs / 1000.0 for s in sources if s.audio is not None)

    # -- windowing ---------------------------------------------------------
    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        self._configure(data.data)
        return self.window(data)

    def exec(self, data: PipelineContainer) -> PipelineContainer:
        if self.window_ms is None:
            self._configure(data.data)
        return self.window(data)

    def window(self, data: PipelineContainer) -> PipelineContainer:
        from app.DataProcessor.DataLoader.media import load_audio

        sources = data.data
        seconds = self.audio_seconds(sources) if self.audio_rate else 0
        if seconds > AUDIO_MAX_TOTAL_SECONDS:
            raise WindowingError(
                f"The selected recordings are {seconds / 3600:.1f} h long; this server trains on at most "
                f"{AUDIO_MAX_TOTAL_SECONDS / 3600:.1f} h of audio. Select fewer datasets.")
        plans = self.plan(sources)
        total = sum(len(starts) for starts, _ in plans)
        if total > MAX_TRAIN_WINDOWS:
            raise WindowingError(
                f"The settings give {total} windows; this server trains on at most {MAX_TRAIN_WINDOWS}. "
                f"Use a larger window step or fewer datasets.")

        rows, labels, metas = [], [], []
        width = HEADER + self.sensor_samples * len(self.channels)
        self.release()
        with _ACTIVE_LOCK:
            self.key = next(_KEYS)
            _ACTIVE[self.key] = self
        for index, (source, (starts, window_labels_)) in enumerate(zip(sources, plans)):
            if len(starts) == 0:
                continue
            block = np.zeros((len(starts), width), dtype=np.float64)
            block[:, 0] = self.key
            block[:, 1] = index
            keep = np.ones(len(starts), dtype=bool)
            if self.audio_rate:
                pcm = load_audio(source.audio.id, self.audio_rate)
                self._audio[index] = pcm
                first = np.round((starts - source.audio.start) * self.audio_rate / 1000.0).astype(np.int64)
                keep &= (first >= 0) & (first + self.audio_samples <= len(pcm))
                block[:, 2] = first
            if self.channels:
                grid = starts[:, None] + np.arange(self.sensor_samples)[None, :] * (self.window_ms / self.sensor_samples)
                for c, (times, values) in enumerate(source.load_sensors()):
                    if len(times) == 0:
                        keep[:] = False
                        continue
                    # windows reaching past a channel's data are not used, no extrapolation
                    keep &= (grid[:, 0] >= times[0] - 1) & (grid[:, -1] <= times[-1] + 1)
                    block[:, HEADER + c: width: len(self.channels)] = np.interp(grid, times, values)
            rows.append(block[keep])
            labels.append(window_labels_[keep])
            metas.extend([source.meta] * int(keep.sum()))
        if not rows or sum(len(r) for r in rows) == 0:
            raise WindowingError("No labeled windows fit into the selected recordings. Use a shorter window, "
                                 "or check that the labels lie where the recordings are.")
        X = np.concatenate(rows)
        Y = np.concatenate(labels)
        self.input_shape = None
        self.output_shape = [int(X.shape[1])]
        return PipelineContainer(X, Y, metas)

    def audio_for(self, rows) -> np.ndarray:
        """(n, audio_samples) float32 audio in [-1, 1] for windower rows."""
        out = np.zeros((len(rows), self.audio_samples), dtype=np.float32)
        for i, (dataset, first) in enumerate(np.asarray(rows)[:, 1:HEADER].astype(np.int64)):
            pcm = self._audio.get(int(dataset))
            if pcm is None:
                raise WindowingError("The audio of this pipeline is no longer loaded.")
            out[i] = pcm[first:first + self.audio_samples] / 32768.0
        return out

    def sensors_for(self, rows) -> np.ndarray:
        """(n, sensor_samples, channels) float32 sensor windows for windower rows."""
        rows = np.asarray(rows)
        return rows[:, HEADER:].astype(np.float32).reshape(len(rows), self.sensor_samples, len(self.channels))

    def release(self):
        """Drop the decoded audio (end of a training run)."""
        with _ACTIVE_LOCK:
            _ACTIVE.pop(self.key, None)
        self._audio = {}

    # -- persistence -------------------------------------------------------
    def get_state(self):
        return {
            "window_ms": self.window_ms,
            "stride_ms": self.stride_ms,
            "sensor_rate": self.sensor_rate,
            "sensor_samples": self.sensor_samples,
            "audio_rate": self.audio_rate,
            "audio_samples": self.audio_samples,
            "channels": self.channels,
            "audio_name": self.audio_name,
        }

    def restore(self, config):
        state = config.state or {}
        self.window_ms = state.get("window_ms")
        self.stride_ms = state.get("stride_ms")
        self.sensor_rate = state.get("sensor_rate")
        self.sensor_samples = int(state.get("sensor_samples") or 0)
        self.audio_rate = state.get("audio_rate")
        self.audio_samples = int(state.get("audio_samples") or 0)
        self.channels = list(state.get("channels") or [])
        self.audio_name = state.get("audio_name")
        super().restore(config)

    # -- export ------------------------------------------------------------
    def export_inputs(self):
        """What the exported model takes, in order (see manifest_v2)."""
        inputs = []
        if self.channels:
            inputs.append({"name": "raw_window", "kind": "sensors",
                           "shape": [1, self.sensor_samples, len(self.channels)],
                           "sampling_rate": self.sensor_rate})
        if self.audio_rate:
            inputs.append({"name": "audio", "kind": "audio", "shape": [1, self.audio_samples],
                           "sample_rate": int(self.audio_rate)})
        return inputs
