from fastapi import APIRouter
from backend.schemas import SearchRequest
from backend.services.search_service import filter_units
from backend.services.query_parser import parse_search_query
from backend.storage.in_memory_store import UNITS_DB

router = APIRouter()


@router.post("/search")
def search(filters: SearchRequest):
    print("UNITS COUNT:", len(UNITS_DB)) 

    parsed = parse_search_query(filters.query)

    if parsed["max_price"] is not None:
        filters.max_price = parsed["max_price"]

    if parsed["bedrooms"] is not None:
        filters.min_bedrooms = parsed["bedrooms"]

    results = filter_units(
    UNITS_DB,
    min_price=filters.min_price,
    max_price=filters.max_price,
    bedrooms=filters.min_bedrooms
    )

    return {
        "count": len(results),
        "results": results
    }