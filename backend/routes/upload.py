from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.services.column_mapper import normalize_columns
from backend.services.value_parser import parse_price, parse_bedrooms, parse_area
from backend.services.column_detector import detect_column
from backend.services.header_detector import detect_header_row

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

    parsed_prices = []
    parsed_bedrooms = []
    parsed_areas = []
    
    # find the original excel column for bedrooms
    bedrooms_column = detect_column(normalized_columns, "bedrooms")
    # find the original excel column for price
    price_column = detect_column(normalized_columns, "price_total")
    # find the original excel column for area
    area_column = detect_column(normalized_columns, "area_m2")
    
    
    # parse values only if a price column is found
    if price_column:
        # loop over each value in the detected column
        for value in df[price_column]:
           # convert messy text to clean number
           parsed_value = parse_price(value)

           # store result in list
           parsed_prices.append(parsed_value)

    # parse values only if a bedrooms column is found
    if bedrooms_column:
    # loop over each value in the detected column
        for value in df[bedrooms_column]:
          # convert messy text to clean number
          parsed_value = parse_bedrooms(value)

          # store result in list
          parsed_bedrooms.append(parsed_value)    
        
    # parse values only if an area column is found
    if area_column:
       # loop over each value in the detected column
       for value in df[area_column]:
           # convert messy text to clean number
           parsed_value = parse_area(value)

           # store result in list
           parsed_areas.append(parsed_value)
         
        
    #return file metadata
    return{
        "filename": file.filename,
        "rows": rows,
        "columns": columns,
        "normalized_columns": normalized_columns,
        "parsed_prices_sample": parsed_prices[:5],  # just preview first 5
        "parsed_bedrooms_sample": parsed_bedrooms[:5],
        "parsed_areas_sample": parsed_areas[:5]
    }