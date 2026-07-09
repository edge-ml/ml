"""Computes which download formats a trained model actually supports.

The result is persisted on the model document at train time and drives the
format dropdown in the frontend download modal. A format is only advertised
when every relevant pipeline step can really be exported — get_platforms()
declarations alone are not reliable (some options declare C support without
implementing exportC)."""

from typing import List

from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.Pipelines.Abstract.StepType import StepType
from app.ml.PipelineExport.Executorch.support import supportsExecutorch


def _supportsC(option) -> bool:
    cls = type(option)
    declares_c = any(
        str(getattr(platform, "value", platform)).lower() in ("c", "cpp")
        for platform in cls.get_platforms()
    )
    implements_c = cls.exportC is not AbstractPipelineOption.exportC
    return declares_c and implements_c


def computeFormats(options) -> List[str]:
    formats = []
    pre_core = [x for x in options if x.type in (StepType.PRE, StepType.CORE)]
    if pre_core and all(_supportsC(x) for x in pre_core):
        formats.append("C")
    if supportsExecutorch(options):
        formats.append("EXECUTORCH")
    return formats
