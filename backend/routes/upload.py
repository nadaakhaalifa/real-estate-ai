from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
import pandas as pd
from backend.services.column_mapper import normalize_columns
from backend.services.value_parser import parse_price, parse_bedrooms, parse_area
from backend.services.column_detector import detect_column
from backend.services.header_detector import detect_header_row
from backend.schemas import UnitPreview

from typing import Annotated
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Upload, Unit
from io import BytesIO

router = APIRouter()


def clean_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text if text else None


def find_bedroom_source_columns(df):
    bedroom_source_columns = []

    keywords = [
        "bed",
        "bedroom",
        "bedrooms",
        "br",
        "bd",
        "category",
        "layout",
        "unit type",
        "type",
        "description",
        "unit name",
        "model",
    ]

    for column in df.columns:
        column_name = str(column).lower().strip()

        if any(keyword in column_name for keyword in keywords):
            bedroom_source_columns.append(column)

    return bedroom_source_columns


def parse_single_file(file: UploadFile, display_name: str):
    try:
        contents = file.file.read()
        file_buffer = BytesIO(contents)

        header_row = detect_header_row(file_buffer)

        file_buffer.seek(0)

        df = pd.read_excel(file_buffer, header=header_row)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file '{file.filename}': {str(e)}"
        )

    rows = len(df)
    columns = list(df.columns)
    normalized_columns = normalize_columns(df.columns)

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

    bedroom_source_columns = find_bedroom_source_columns(df)

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

    if bedrooms_column:
        df[bedrooms_column] = df[bedrooms_column].ffill()

    for column in bedroom_source_columns:
        if column != bedrooms_column:
            df[column] = df[column].ffill()

    for _, row in df.iterrows():
        price = parse_price(row[price_column]) if price_column else None
        area = parse_area(row[area_column]) if area_column else None

        location = clean_text(row[location_column]) if location_column else None
        stage = clean_text(row[stage_column]) if stage_column else None
        developer_name = clean_text(row[developer_column]) if developer_column else None
        unit_type = clean_text(row[unit_type_column]) if unit_type_column else None
        building = clean_text(row[building_column]) if building_column else None
        project_name = clean_text(row[project_column]) if project_column else None
        unit_code = clean_text(row[unit_code_column]) if unit_code_column else None

        bedrooms = None

        bedroom_sources = []

        if bedrooms_column:
            bedroom_sources.append(row[bedrooms_column])

        for column in bedroom_source_columns:
            if column != bedrooms_column:
                bedroom_sources.append(row[column])

        if unit_type_column and unit_type_column not in bedroom_source_columns:
            bedroom_sources.append(row[unit_type_column])

        for raw_bedroom in bedroom_sources:
            bedrooms = parse_bedrooms(raw_bedroom)
            if bedrooms is not None:
                break

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
            source_file=display_name,
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

        unit_data = unit.model_dump()
        unit_data["source_file"] = display_name

        unit_previews.append(unit_data)

    return {
        "filename": file.filename,
        "display_name": display_name,
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
            "bedroom_source_columns": bedroom_source_columns,
        },
        "units": unit_previews,
    }


@router.post("/upload")
async def upload_files(
    files: Annotated[list[UploadFile], File(...)],
    display_names: Annotated[list[str], Form(...)],
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if len(display_names) != len(files):
        raise HTTPException(status_code=400, detail="Mismatch files and names")

    db.query(Unit).delete()
    db.query(Upload).delete()
    db.commit()

    for file, display_name in zip(files, display_names):
        result = parse_single_file(file, display_name)

        upload_record = Upload(filename=display_name)
        db.add(upload_record)
        db.flush()

        for unit_data in result["units"]:
            unit = Unit(
                upload_id=upload_record.id,
                developer_name=unit_data.get("developer_name"),
                project_name=unit_data.get("project_name"),
                location=unit_data.get("location"),
                stage=unit_data.get("stage"),
                unit_type=unit_data.get("unit_type"),
                bedrooms=unit_data.get("bedrooms"),
                area_m2=unit_data.get("area_m2"),
                price_total=unit_data.get("price_total"),
                building=unit_data.get("building"),
                unit_code=unit_data.get("unit_code"),
                source_file=display_name,
                raw_data=unit_data.get("raw_data", {}),
            )
            db.add(unit)

    db.commit()

    return {"message": "Upload successful"}