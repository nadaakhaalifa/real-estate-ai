from fastapi import FastAPI, APIRouter, UploadFile, File
import pandas as pd

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
    
    #return file metadata
    return{
        "filename": file.filename,
        "rows": rows,
        "columns": columns
    }