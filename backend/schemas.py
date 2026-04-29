from pydantic import BaseModel, Field
from typing import Any
from typing import Optional



# clean extracted unit data 
class UnitPreview(BaseModel):
    developer_name: str | None = None
    project_name: str | None = None
    location: str | None = None
    district: str | None = None
    stage: str | None = None
    unit_type: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_m2: float | None = None
    price_total: float | None = None
    price_per_m2: float | None = None
    delivery_date: str | None = None
    finishing_status: str | None = None
    building: str | None = None
    floor_number: str | None = None
    unit_code: str | None = None
    source_file: Optional[str] = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    
# request schema for search endpoint
class SearchRequest(BaseModel):
    query: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_bedrooms: int | None = None
    max_bedrooms: int | None = None
    min_area: float | None = None
    max_area: float | None = None
    developer_name: str | None = None
    location: str | None = None
    project_name: str | None = None
    unit_type: str | None = None
    stage: str | None = None
    sort_by: str = "price_total"
    sort_order: str = "asc"
    
    page: int = 1
    page_size: int = 20