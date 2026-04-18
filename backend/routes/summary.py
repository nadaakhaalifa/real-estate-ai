from fastapi import APIRouter
from backend.storage.in_memory_store import UNITS_DB
from backend.services.summary_builder import build_summary

router = APIRouter()


# return grouped bedroom summary from uploaded units
@router.get("/summary")
def get_summary():
    summary_rows = build_summary(UNITS_DB)

    return {
        "total_units": len(UNITS_DB),
        "summary_rows": summary_rows,
    }