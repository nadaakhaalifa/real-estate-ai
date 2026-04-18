from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from backend.services.column_mapper import normalize_columns
from backend.services.value_parser import parse_price, parse_bedrooms, parse_area
from backend.services.column_detector import detect_column
from backend.services.header_detector import detect_header_row
from backend.schemas import UnitPreview
from backend.storage.in_memory_store import UNITS_DB
from typing import Annotated

# create router
router = APIRouter()


# clean any text value (remove spaces, handle NaN)
def clean_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text if text else None


# parse one excel file and return extracted units + summary
def parse_single_file(file: UploadFile):
    try:
        # detect header row dynamically
        header_row = detect_header_row(file.file)

        # reset pointer after reading
        file.file.seek(0)

        # load excel into dataframe
        df = pd.read_excel(file.file, header=header_row)

        print("COLUMNS:", [repr(c) for c in df.columns.tolist()])
        print("DTYPES:")
        print(df.dtypes)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file '{file.filename}': {str(e)}"
        )

    rows = len(df)
    columns = list(df.columns)
    normalized_columns = normalize_columns(df.columns)

    # track used columns to avoid duplicates
    used_columns = set()

    # detect columns dynamically
    project_column = detect_column(df, "project_name", used_columns)
    if project_column:
        used_columns.add(project_column)

    unit_code_column = detect_column(df, "unit_code", used_columns)
    if unit_code_column:
        used_columns.add(unit_code_column)

    building_column = detect_column(df, "building", used_columns)
    if building_column:
        used_columns.add(building_column)

    unit_type_column = detect_column(df, "unit_type", used_columns)
    if unit_type_column:
        used_columns.add(unit_type_column)

    developer_column = detect_column(df, "developer_name", used_columns)
    if developer_column:
        used_columns.add(developer_column)

    location_column = detect_column(df, "location", used_columns)
    if location_column:
        used_columns.add(location_column)

    stage_column = detect_column(df, "stage", used_columns)
    if stage_column:
        used_columns.add(stage_column)

    price_column = detect_column(df, "price_total", used_columns)
    if price_column:
        used_columns.add(price_column)

    bedrooms_column = detect_column(df, "bedrooms", used_columns)
    if bedrooms_column:
        used_columns.add(bedrooms_column)

    area_column = detect_column(df, "area_m2", used_columns)
    if area_column:
        used_columns.add(area_column)

    unit_previews = []
    
    # temporary fix if exported sheet has intermittent blank bedroom cells
    if bedrooms_column: 
      df[bedrooms_column] = df[bedrooms_column].ffill()
      
    # loop over rows and build structured units
    for _, row in df.iterrows():
        price = parse_price(row[price_column]) if price_column else None

        raw_bedroom = row[bedrooms_column] if bedrooms_column else None
        bedrooms = parse_bedrooms(raw_bedroom) if bedrooms_column else None
        area = parse_area(row[area_column]) if area_column else None

        location = clean_text(row[location_column]) if location_column else None
        stage = clean_text(row[stage_column]) if stage_column else None
        developer_name = clean_text(row[developer_column]) if developer_column else None
        unit_type = clean_text(row[unit_type_column]) if unit_type_column else None
        building = clean_text(row[building_column]) if building_column else None
        project_name = clean_text(row[project_column]) if project_column else None
        unit_code = clean_text(row[unit_code_column]) if unit_code_column else None

        # fallback: try extracting bedrooms from unit_type
        if bedrooms is None and unit_type:
            bedrooms = parse_bedrooms(unit_type)

        # skip empty rows
        if (
            price is None
            and bedrooms is None
            and area is None
            and location is None
            and stage is None
            and developer_name is None
            and unit_type is None
            and building is None
            and project_name is None
            and unit_code is None
        ):
            continue

        # build unit object
        unit = UnitPreview(
            source_file=file.filename,
            developer_name=developer_name,
            location=location,
            stage=stage,
            price_total=price,
            bedrooms=bedrooms,
            area_m2=area,
            unit_type=unit_type,
            project_name=project_name,
            building=building,
            unit_code=unit_code,
        )

        unit_previews.append(unit.model_dump(exclude_none=True))

    return {
        "filename": file.filename,
        "rows": rows,
        "columns": columns,
        "normalized_columns": normalized_columns,
        "detected_columns": {
            "price_total": price_column,
            "bedrooms": bedrooms_column,
            "area_m2": area_column,
            "location": location_column,
            "stage": stage_column,
            "developer_name": developer_column,
            "unit_type": unit_type_column,
            "project_name": project_column,
            "unit_code": unit_code_column,
            "building": building_column,
        },
        "units": unit_previews,
    }


@router.post("/upload")
async def upload_files(
    files: Annotated[
        list[UploadFile],
        File(..., description="Upload up to 50 Excel files")
    ]
):
    # validate input
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Max 50 files allowed")

    # allow only excel files
    allowed_extensions = (".xlsx", ".xls")

    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="One uploaded file has no filename")

        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )

    all_units = []
    uploaded_files_summary = []

    # process each file
    for file in files:
        result = parse_single_file(file)

        # collect all units
        all_units.extend(result["units"])

        # collect file summary
        uploaded_files_summary.append({
            "filename": result["filename"],
            "rows": result["rows"],
            "units_extracted": len(result["units"]),
            "detected_columns": result["detected_columns"],
        })

    # store all data in memory
    UNITS_DB.clear()
    UNITS_DB.extend(all_units)

    print("TOTAL UNITS STORED:", len(UNITS_DB))

    # return response
    return {
        "files_uploaded": len(files),
        "total_units": len(UNITS_DB),
        "files": uploaded_files_summary,
        "sample_units": UNITS_DB[:10],
    }