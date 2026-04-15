from pydantic import BaseModel
from typing import Optional


# clean extracted unit data 
class UnitPreview(BaseModel):
    price_total: float | None = None
    bedrooms: int | None = None
    area_m2: float | None = None
    
# request schema for search endpoint
class SearchRequest(BaseModel):
    query: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[float] = None
    max_bedrooms: Optional[float] = None