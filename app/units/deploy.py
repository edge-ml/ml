"""Unit information shipped with every model export.

Each input channel lists the quantity and unit the model expects and, for
built-in quantities, the affine conversion from every catalog unit of that
quantity. Apps (or the edge-ml libraries) apply ``expected = value * scale +
offset`` for the unit their sensor delivers, without needing the catalog.
"""

from typing import List

from app.units.catalog import conversion, get_quantity


def input_units(model) -> List[dict]:
    if not getattr(model, "inputUnits", None):
        # Trained before units existed: nothing is known about the inputs.
        return [{"name": name, "quantity": None, "unit": "", "conversions": {}}
                for name in (model.timeSeries or [])]

    res = []
    for inp in model.inputUnits:
        quantity = get_quantity(inp.quantity)
        conversions = {}
        if quantity is not None and quantity.unit(inp.unit):
            for u in quantity.units:
                scale, offset = conversion(quantity, u.id, inp.unit)
                conversions[u.id] = {"scale": scale, "offset": offset}
        res.append({"name": inp.name, "quantity": inp.quantity, "unit": inp.unit,
                    "conversions": conversions})
    return res


def units_summary(model) -> str:
    """One line per channel, for READMEs and generated source comments."""
    lines = []
    for u in input_units(model):
        if u["quantity"] is None and not u["unit"]:
            lines.append(f"{u['name']}: unit unknown, feed values as recorded")
        else:
            what = u["quantity"] or "custom"
            lines.append(f"{u['name']}: {u['unit'] or 'no unit'} ({what})")
    return "\n".join(lines)
