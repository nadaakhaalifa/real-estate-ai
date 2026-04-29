from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from backend.services.summary_builder import build_summary
from backend.services.pdf_generator import generate_summary_pdf
from backend.services.excel_generator import generate_summary_excel

from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Unit


router = APIRouter()


ALLOWED_SORT_KEYS = {
    "source_file",
    "project_name",
    "category_value",
    "starting_price",
    "starting_area_m2",
}


def serialize_units(units):
    units_data = []

    for unit in units:
        units_data.append({
            "developer_name": unit.developer_name,
            "project_name": unit.project_name,
            "location": unit.location,
            "district": unit.district,
            "stage": unit.stage,
            "unit_type": unit.unit_type,
            "bedrooms": unit.bedrooms,
            "bathrooms": unit.bathrooms,
            "area_m2": unit.area_m2,
            "price_total": unit.price_total,
            "price_per_m2": unit.price_per_m2,
            "delivery_date": unit.delivery_date,
            "finishing_status": unit.finishing_status,
            "building": unit.building,
            "floor_number": unit.floor_number,
            "unit_code": unit.unit_code,
            "source_file": unit.source_file or (unit.upload.filename if unit.upload else None),
            "raw_data": unit.raw_data,
        })

    return units_data


def filter_and_sort_summary_rows(
    summary_rows,
    search="",
    category="all",
    sort_key="source_file",
    sort_direction="asc",
):
    rows = summary_rows[:]

    search = (search or "").strip()
    category = str(category or "all").strip()
    sort_key = sort_key if sort_key in ALLOWED_SORT_KEYS else "source_file"
    sort_direction = "desc" if str(sort_direction).lower() == "desc" else "asc"

    if search:
        search_lower = search.lower()

        rows = [
            row for row in rows
            if (
                search_lower in str(row.get("source_file") or "").lower()
                or search_lower in str(row.get("project_name") or "").lower()
                or search_lower in str(row.get("developer_name") or "").lower()
            )
        ]

    if category != "all":
        rows = [
            row for row in rows
            if str(row.get("category_value")) == category
        ]

    reverse = sort_direction == "desc"

    def sort_value(row):
        value = row.get(sort_key)

        if sort_key in {"source_file", "project_name"}:
            return str(value or "").lower()

        if sort_key in {"category_value", "starting_price", "starting_area_m2"}:
            return value if value is not None else 0

        return value

    rows.sort(key=sort_value, reverse=reverse)
    return rows


def build_filtered_summary_rows(
    db: Session,
    search="",
    category="all",
    sort_key="source_file",
    sort_direction="asc",
):
    units = db.query(Unit).all()
    units_data = serialize_units(units)
    summary_rows = build_summary(units_data)

    filtered_rows = filter_and_sort_summary_rows(
        summary_rows=summary_rows,
        search=search,
        category=category,
        sort_key=sort_key,
        sort_direction=sort_direction,
    )

    return units_data, filtered_rows


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    search: str = Query(default=""),
    category: str = Query(default="all"),
    sort_key: str = Query(default="source_file"),
    sort_direction: str = Query(default="asc"),
):
    units_data, filtered_rows = build_filtered_summary_rows(
        db=db,
        search=search,
        category=category,
        sort_key=sort_key,
        sort_direction=sort_direction,
    )

    return {
        "total_units": len(units_data),
        "summary_rows": filtered_rows,
    }


@router.get("/summary/pdf")
def get_summary_pdf(
    db: Session = Depends(get_db),
    search: str = Query(default=""),
    category: str = Query(default="all"),
    sort_key: str = Query(default="source_file"),
    sort_direction: str = Query(default="asc"),
):
    _, filtered_rows = build_filtered_summary_rows(
        db=db,
        search=search,
        category=category,
        sort_key=sort_key,
        sort_direction=sort_direction,
    )

    pdf_buffer = generate_summary_pdf(filtered_rows)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=summary_report.pdf"},
    )


@router.get("/summary/excel")
def get_summary_excel(
    db: Session = Depends(get_db),
    search: str = Query(default=""),
    category: str = Query(default="all"),
    sort_key: str = Query(default="source_file"),
    sort_direction: str = Query(default="asc"),
):
    _, filtered_rows = build_filtered_summary_rows(
        db=db,
        search=search,
        category=category,
        sort_key=sort_key,
        sort_direction=sort_direction,
    )

    excel_buffer = generate_summary_excel(filtered_rows)

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=summary_report.xlsx"},
    )