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
    bedrooms_column = detect_column(df, "bedrooms")
    price_column = detect_column(df, "price_total")
    area_column = detect_column(df, "area_m2")
    
    #Add debug prints to find out why some files fail
    print("HEADER ROW:", header_row)
    print("DETECTED PRICE COLUMN:", price_column)
    print("DETECTED BEDROOMS COLUMN:", bedrooms_column)
    print("DETECTED AREA COLUMN:", area_column)
    
    
       # build parsed units row by row
    unit_previews = []

    for _, row in df.iterrows():
        price = parse_price(row[price_column]) if price_column else None
        bedrooms = parse_bedrooms(row[bedrooms_column]) if bedrooms_column else None
        area = parse_area(row[area_column]) if area_column else None

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

    # return upload summary
    return {
        "filename": file.filename,
        "rows": rows,
        "columns": columns,
        "normalized_columns": normalized_columns,
        "detected_columns": {
            "price_total": price_column,
            "bedrooms": bedrooms_column,
            "area_m2": area_column
        },
        "unit_previews_sample": unit_previews[:5]
    }