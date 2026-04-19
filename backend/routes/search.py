from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas import SearchRequest
from backend.services.query_parser import parse_search_query
from backend.database import get_db
from backend.models import Unit

router = APIRouter()


@router.post("/search")
def search(filters: SearchRequest, db: Session = Depends(get_db)):
    units_count = db.query(Unit).count()
    print("UNITS COUNT:", units_count)

    if units_count == 0:
        return {
            "count": 0,
            "total_count": 0,
            "page": filters.page,
            "page_size": filters.page_size,
            "results": [],
            "message": "No units uploaded yet"
        }

    parsed = parse_search_query(filters.query.strip()) if filters.query and filters.query.strip() else {}
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

    if parsed.get("developer_name") and not filters.developer_name:
        filters.developer_name = parsed["developer_name"]

    if parsed.get("stage") and not filters.stage:
        filters.stage = parsed["stage"]

    if parsed.get("min_area") is not None and filters.min_area is None:
        filters.min_area = parsed["min_area"]

    if parsed.get("max_area") is not None and filters.max_area is None:
        filters.max_area = parsed["max_area"]

    if filters.page < 1:
        filters.page = 1

    if filters.page_size < 1:
        filters.page_size = 20

    if filters.page_size > 100:
        filters.page_size = 100

    query = db.query(Unit)

    if filters.min_price is not None:
        query = query.filter(Unit.price_total >= filters.min_price)

    if filters.max_price is not None:
        query = query.filter(Unit.price_total <= filters.max_price)

    if filters.min_bedrooms is not None:
        query = query.filter(Unit.bedrooms >= filters.min_bedrooms)

    if filters.max_bedrooms is not None:
        query = query.filter(Unit.bedrooms <= filters.max_bedrooms)

    if filters.min_area is not None:
        query = query.filter(Unit.area_m2 >= filters.min_area)

    if filters.max_area is not None:
        query = query.filter(Unit.area_m2 <= filters.max_area)

    if filters.project_name:
        query = query.filter(Unit.project_name.ilike(f"%{filters.project_name}%"))

    if filters.location:
        query = query.filter(Unit.location.ilike(f"%{filters.location}%"))

    if filters.unit_type:
        query = query.filter(Unit.unit_type.ilike(f"%{filters.unit_type}%"))

    if filters.stage:
        query = query.filter(Unit.stage.ilike(f"%{filters.stage}%"))

    if filters.developer_name:
        query = query.filter(Unit.developer_name.ilike(f"%{filters.developer_name}%"))

    total_count = query.count()

    offset = (filters.page - 1) * filters.page_size

    units = query.order_by(Unit.price_total.asc().nullslast()).offset(offset).limit(filters.page_size).all()

    results = []

    for unit in units:
        results.append({
            "id": unit.id,
            "developer_name": unit.developer_name,
            "project_name": unit.project_name,
            "location": unit.location,
            "district": unit.district,
            "stage": unit.stage,
            "unit_type": unit.unit_type,
            "bedrooms": unit.bedrooms,
            "bathrooms": unit.bathrooms,
            "area_m2": unit.area_m2,
            "price_total": unit.price_total,
            "price_per_m2": unit.price_per_m2,
            "delivery_date": unit.delivery_date,
            "finishing_status": unit.finishing_status,
            "building": unit.building,
            "floor_number": unit.floor_number,
            "unit_code": unit.unit_code,
            "source_file": unit.source_file,
            "raw_data": unit.raw_data,
        })

    print("TOTAL COUNT:", total_count)
    print("RESULT COUNT:", len(results))
    print("PAGE:", filters.page)
    print("PAGE SIZE:", filters.page_size)

    return {
        "count": len(results),
        "total_count": total_count,
        "page": filters.page,
        "page_size": filters.page_size,
        "results": results
    }