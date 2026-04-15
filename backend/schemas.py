from pydantic import BaseModel

# clean extracted unit data 
class UnitPreview(BaseModel):
    price_total: float | None = None
    bedrooms: int | None = None
    area_m2: float | None = None
    