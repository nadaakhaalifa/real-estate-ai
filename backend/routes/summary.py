from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.storage.in_memory_store import UNITS_DB
from backend.services.summary_builder import build_summary
from backend.services.pdf_generator import generate_summary_pdf

router = APIRouter()


# return grouped summary as json
@router.get("/summary")
def get_summary():
    summary_rows = build_summary(UNITS_DB)

    return {
        "total_units": len(UNITS_DB),
        "summary_rows": summary_rows,
    }


# return grouped summary as pdf
@router.get("/summary/pdf")
def get_summary_pdf():
    summary_rows = build_summary(UNITS_DB)
    pdf_buffer = generate_summary_pdf(summary_rows)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=summary_report.pdf"},
    )