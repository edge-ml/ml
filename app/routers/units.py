from fastapi import APIRouter

from app.units.catalog import catalog_json

router = APIRouter()


@router.get("/")
async def get_unit_catalog():
    # Static reference data, so no project or API key is needed.
    return catalog_json()
