from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.services.column_mapper import normalize_columns
from backend.services.value_parser import parse_price, parse_bedrooms, parse_area
from backend.services.column_detector import detect_column
from backend.services.header_detector import detect_header_row
from backend.schemas import UnitPreview
from backend.storage.in_memory_store import UNITS_DB

# create router for upload endpoints
router = APIRouter()

# API endpoint [post => send file]
@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    # detect correct header row
    header_row = detect_header_row(file.file)

    # reset file pointer (VERY IMPORTANT)
    file.file.seek(0)

    # read excel into dataframe with correct header
    df = pd.read_excel(file.file, header=header_row)
    
    #count rows
    rows= len(df)
    
    #get all column names
    columns = list(df.columns)
    
    # normalize column names
    normalized_columns = normalize_columns(df.columns)

    # parsed values
    parsed_prices = []
    parsed_bedrooms = []
    parsed_areas = []
    

    # find original excel columns
    bedrooms_column = detect_column(normalized_columns, "bedrooms")
    price_column = detect_column(normalized_columns, "price_total")
    area_column = detect_column(normalized_columns, "area_m2")
    
    
    # parse prices
    if price_column:
        for value in df[price_column]:
           parsed_value = parse_price(value)
           parsed_prices.append(parsed_value)

    # parse bedrooms
    if bedrooms_column:
        for value in df[bedrooms_column]:
          parsed_value = parse_bedrooms(value)
          parsed_bedrooms.append(parsed_value)    
        
    # parse areas
    if area_column:
       for value in df[area_column]:
           parsed_value = parse_area(value)
           parsed_areas.append(parsed_value)
        
        
    # combine parsed values into preview objects
    # "Take price + bedroom + area → combine into ONE object" 
    unit_previews = []

    # get max length between all lists
    max_length = max(len(parsed_prices), len(parsed_bedrooms), len(parsed_areas), 0)

    # build one preview object per index
    for i in range(max_length):
        price = parsed_prices[i] if i < len(parsed_prices) else None
        bedrooms = parsed_bedrooms[i] if i < len(parsed_bedrooms) else None
        area = parsed_areas[i] if i < len(parsed_areas) else None

        # skip completely empty rows
        if price is None and bedrooms is None and area is None:
            continue

        unit = UnitPreview(
            price_total=price,
            bedrooms=bedrooms,
            area_m2=area
        )

        unit_previews.append(unit.model_dump())
    
    # store uploaded units in memory for search
    UNITS_DB.clear()
    UNITS_DB.extend(unit_previews)

    print("UPLOADED UNITS:", len(UNITS_DB))   
        
        
    #return file metadata
    return{
        "filename": file.filename,
        "rows": rows,
        "columns": columns,
        "normalized_columns": normalized_columns,
        "parsed_prices_sample": parsed_prices[:5],  # just preview first 5
        "parsed_bedrooms_sample": parsed_bedrooms[:5],
        "parsed_areas_sample": parsed_areas[:5],
        "unit_previews_sample": unit_previews[:5]
    }