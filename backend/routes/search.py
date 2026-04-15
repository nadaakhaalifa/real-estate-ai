from fastapi import APIRouter
from backend.schemas import SearchRequest
from backend.services.search_service import filter_units
from backend.services.query_parser import parse_search_query
from backend.storage.in_memory_store import UNITS_DB

router = APIRouter()


@router.post("/search")
def search(filters: SearchRequest):
    print("UNITS COUNT:", len(UNITS_DB))

    parsed = parse_search_query(filters.query) if filters.query else {}
    print("PARSED QUERY:", parsed)

    if parsed.get("max_price") is not None and filters.max_price is None:
        filters.max_price = parsed["max_price"]

    if parsed.get("bedrooms") is not None and filters.min_bedrooms is None:
        filters.min_bedrooms = parsed["bedrooms"]

    if parsed.get("location") and not filters.location:
        filters.location = parsed["location"]

    if parsed.get("project_name") and not filters.project_name:
        filters.project_name = parsed["project_name"]

    if parsed.get("unit_type") and not filters.unit_type:
        filters.unit_type = parsed["unit_type"]

    results = filter_units(
        UNITS_DB,
        min_price=filters.min_price,
        max_price=filters.max_price,
        min_bedrooms=filters.min_bedrooms,
        max_bedrooms=filters.max_bedrooms,
        min_area=filters.min_area,
        max_area=filters.max_area,
        project_name=filters.project_name,
        location=filters.location,
        unit_type=filters.unit_type,
        stage=filters.stage,
        developer_name=filters.developer_name,
    )

    print("RESULT COUNT:", len(results))

    return {
        "count": len(results),
        "results": results
    }