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


def clean_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text if text else None


# API endpoint [post => send file]
@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    # detect correct header row
    header_row = detect_header_row(file.file)

    # reset file pointer (VERY IMPORTANT)
    file.file.seek(0)

    # read excel into dataframe with correct header
    df = pd.read_excel(file.file, header=header_row)

    # count rows
    rows = len(df)

    # get all column names
    columns = list(df.columns)

    # normalize column names
    normalized_columns = normalize_columns(df.columns)

    # find original excel columns
    # bedrooms_column = detect_column(df, "bedrooms")
    # price_column = detect_column(df, "price_total")
    # area_column = detect_column(df, "area_m2")
    # location_column = detect_column(df, "location")
    # stage_column = detect_column(df, "stage")
    # developer_column = detect_column(df, "developer_name")
    # unit_type_column = detect_column(df, "unit_type")
    # building_column = detect_column(df, "building")
    # project_column = detect_column(df, "project_name")
    # unit_code_column = detect_column(df, "unit_code")
    # 🎯 smarter detection with no column reuse
    used_columns = set()

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
    

    # add debug prints to find out why some files fail
    print("HEADER ROW:", header_row)
    print("DETECTED PRICE COLUMN:", price_column)
    print("DETECTED BEDROOMS COLUMN:", bedrooms_column)
    print("DETECTED AREA COLUMN:", area_column)
    print("DETECTED LOCATION COLUMN:", location_column)
    print("DETECTED STAGE COLUMN:", stage_column)
    print("DETECTED DEVELOPER COLUMN:", developer_column)
    print("DETECTED UNIT TYPE COLUMN:", unit_type_column)
    print("DETECTED BUILDING COLUMN:", building_column)
    print("DETECTED PROJECT COLUMN:", project_column)
    print("DETECTED UNIT CODE COLUMN:", unit_code_column)
    
    # build parsed units row by row
    unit_previews = []

    for _, row in df.iterrows():
        price = parse_price(row[price_column]) if price_column else None
        bedrooms = parse_bedrooms(row[bedrooms_column]) if bedrooms_column else None
        area = parse_area(row[area_column]) if area_column else None
        location = clean_text(row[location_column]) if location_column else None
        stage = clean_text(row[stage_column]) if stage_column else None
        developer_name = clean_text(row[developer_column]) if developer_column else None
        unit_type = clean_text(row[unit_type_column]) if unit_type_column else None
        building = clean_text(row[building_column]) if building_column else None
        project_name = clean_text(row[project_column]) if project_column else None
        unit_code = clean_text(row[unit_code_column]) if unit_code_column else None

        # skip completely empty rows
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

        unit = UnitPreview(
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
        "area_m2": area_column,
        "location": location_column,
        "stage": stage_column,
        "developer_name": developer_column,
        "unit_type": unit_type_column,
        "project_name": project_column,
        "unit_code": unit_code_column,
        "building": building_column
        },
        "unit_previews_sample": unit_previews[:10]
    }