"""Work out a model's expected input units and the per-series conversions.

Channels are matched across datasets by time-series name (as training does).
For each channel:

* every dataset has a built-in quantity with a catalog unit (the same quantity
  everywhere): the data is converted to the quantity's default unit, which the
  model then expects;
* every dataset has the quantity unset (unknown): nothing is converted and the
  unit stays whatever label the series carry, as before units existed;
* custom quantities or units must be identical across datasets, since they
  cannot be converted;
* anything else (mixed quantities, known next to unknown, ...) is an error,
  because training on it would silently mix incompatible values.
"""

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel

from app.units.catalog import conversion, get_quantity


class InputUnit(BaseModel):
    """What a model expects for one input channel."""
    name: str
    quantity: Optional[str] = None
    unit: str = ""


class UnitError(Exception):
    pass


Affine = Tuple[float, float]


def _describe(ds_name, ts) -> str:
    q = ts.quantity or "unknown quantity"
    u = ts.unit or "no unit"
    return f"'{ds_name}' ({q}, {u})"


def resolve_units(datasets) -> Tuple[List[InputUnit], Dict[Tuple[str, str], Affine]]:
    """Returns the model's input units (in channel order of the first dataset)
    and the conversions to apply, keyed by (dataset id, time-series id).
    Series without an entry are used as they are."""
    if not datasets:
        return [], {}

    inputs: List[InputUnit] = []
    conversions: Dict[Tuple[str, str], Affine] = {}

    for channel in [ts.name for ts in datasets[0].timeSeries]:
        series = [(ds, next((ts for ts in ds.timeSeries if ts.name == channel), None)) for ds in datasets]
        if any(ts is None for _, ts in series):
            # Channel names differ between datasets; nothing to match units on.
            inputs.append(InputUnit(name=channel))
            continue
        quantities = {ts.quantity or "" for _, ts in series}

        if quantities == {""}:
            units = {ts.unit for _, ts in series}
            inputs.append(InputUnit(name=channel, unit=units.pop() if len(units) == 1 else ""))
            continue

        if len(quantities) > 1:
            listed = ", ".join(_describe(ds.name, ts) for ds, ts in series)
            raise UnitError(
                f"Time-series '{channel}' has different or missing quantities across datasets: {listed}. "
                "Set the same quantity on all of them before training."
            )

        quantity_id = quantities.pop()
        quantity = get_quantity(quantity_id)
        known = quantity is not None and all(quantity.unit(ts.unit) for _, ts in series)

        if known:
            target = quantity.defaultUnit
            for ds, ts in series:
                scale, offset = conversion(quantity, ts.unit, target)
                if (scale, offset) != (1.0, 0.0):
                    conversions[(str(ds.id), str(ts.id))] = (scale, offset)
            inputs.append(InputUnit(name=channel, quantity=quantity_id, unit=target))
            continue

        units = {ts.unit for _, ts in series}
        if len(units) > 1:
            listed = ", ".join(_describe(ds.name, ts) for ds, ts in series)
            raise UnitError(
                f"Time-series '{channel}' uses units that edge-ml cannot convert: {listed}. "
                "Use the same unit everywhere, or pick catalog units so they convert automatically."
            )
        inputs.append(InputUnit(name=channel, quantity=quantity_id, unit=units.pop()))

    return inputs, conversions
