from fastapi import FastAPI, APIRouter, UploadFile, File
import pandas as pd
from backend.services.column_mapper import normalize_columns
from backend.services.value_parser import parse_price
from backend.services.column_detector import detect_column
from backend.services.header_detector import detect_header_row

# create router for upload endpoints
router = APIRouter()

# API endpoint [post => send file]
@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    #read excel into dataframe
    df = pd.read_excel(file.file)
    
    #count rows
    rows= len(df)
    
    #get all column names
    columns = list(df.columns)
    
    # normalize column names
    normalized_columns = normalize_columns(df.columns)
    
    # You are taking messy Excel values and converting them into usable numbers
    # create empty list to store parsed values
    parsed_prices = []
    
    # find the original excel column for price
    price_column = detect_column(normalized_columns, "price_total")
    
    
    # parse values only if a price column is found
    if price_column:
        # loop over each value in the detected column
        for value in df[price_column]:
           # convert messy text to clean number
           parsed_value = parse_price(value)

           # store result in list
           parsed_prices.append(parsed_value)

        
    #return file metadata
    return{
        "filename": file.filename,
        "rows": rows,
        "columns": columns,
        "normalized_columns": normalized_columns,
        "parsed_prices_sample": parsed_prices[:5]  # just preview first 5
    }