from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.services.summary_builder import build_summary
from backend.services.pdf_generator import generate_summary_pdf
from backend.services.excel_generator import generate_summary_excel

from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Unit


router = APIRouter()


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
            "source_file": unit.source_file,
            "raw_data": unit.raw_data,
        })

    return units_data


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    units = db.query(Unit).all()
    units_data = serialize_units(units)
    summary_rows = build_summary(units_data)

    return {
        "total_units": len(units_data),
        "summary_rows": summary_rows,
    }


@router.get("/summary/pdf")
def get_summary_pdf(db: Session = Depends(get_db)):
    units = db.query(Unit).all()
    units_data = serialize_units(units)
    summary_rows = build_summary(units_data)
    pdf_buffer = generate_summary_pdf(summary_rows)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=summary_report.pdf"},
    )


@router.get("/summary/excel")
def get_summary_excel(db: Session = Depends(get_db)):
    units = db.query(Unit).all()
    units_data = serialize_units(units)
    summary_rows = build_summary(units_data)
    excel_buffer = generate_summary_excel(summary_rows)

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=summary_report.xlsx"},
    )