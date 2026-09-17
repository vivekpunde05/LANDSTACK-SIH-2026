import csv
from datetime import datetime, timezone
from io import StringIO

from fastapi import APIRouter, Query
from fastapi.responses import Response

from ..schemas.analytics import AnalyticsCollection, AnalyticsSummary, AttentionCollection
from ..services.analytics import (
    analytics_attention, analytics_distributions, analytics_geography,
    analytics_snapshot, analytics_summary,
)

router = APIRouter(prefix="/api", tags=["governance analytics and reports"])


@router.get("/analytics/summary", response_model=AnalyticsSummary)
def summary() -> dict:
    return analytics_summary()


@router.get("/analytics/distributions", response_model=AnalyticsCollection)
def distributions() -> dict:
    return analytics_distributions()


@router.get("/analytics/geography", response_model=AnalyticsCollection)
def geography() -> dict:
    return analytics_geography()


@router.get("/analytics/attention", response_model=AttentionCollection)
def attention(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return analytics_attention(limit=limit)


def _safe_cell(value) -> str:
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _csv_response(report_name: str, fields: tuple[str, ...], rows: list[dict]) -> Response:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _safe_cell(row.get(field)) for field in fields})
    stamp = datetime.now(timezone.utc).date().isoformat()
    return Response(
        content="\ufeff" + output.getvalue(), media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="landstack_{report_name}_{stamp}.csv"'},
    )


@router.get("/reports/parcels.csv")
def parcel_report() -> Response:
    rows = analytics_snapshot()["parcels"]
    fields = ("parcel_id", "survey_number", "village", "taluka", "district", "area_hectares", "land_type", "land_use", "record_status", "verification_status", "risk_status")
    return _csv_response("parcel_summary", fields, rows)


@router.get("/reports/priorities.csv")
def priority_report() -> Response:
    rows = analytics_snapshot()["priorities"]
    fields = ("rank", "parcel_id", "survey_number", "village", "taluka", "verification_status", "record_status", "review_status", "change_percentage", "priority_score", "priority_level", "score_version")
    return _csv_response("inspection_priority", fields, rows)


@router.get("/reports/grievances.csv")
def grievance_report() -> Response:
    rows = analytics_snapshot()["grievances"]
    fields = ("grievance_id", "parcel_id", "survey_number", "village", "taluka", "category", "custom_category", "status", "submitted_at", "updated_at", "requires_field_verification", "evidence_count", "storage_mode")
    return _csv_response("grievance_summary", fields, rows)


@router.get("/reports/inspections.csv")
def inspection_report() -> Response:
    rows = analytics_snapshot()["inspections"]
    fields = ("inspection_id", "parcel_id", "inspection_status", "inspection_outcome", "inspection_date", "completed_at", "priority_score_at_inspection", "priority_level_at_inspection", "satellite_change_percentage_at_inspection", "requires_follow_up", "evidence_count", "storage_mode")
    return _csv_response("inspection_summary", fields, rows)


@router.get("/reports/cases.csv")
def case_report() -> Response:
    rows = analytics_snapshot()["cases"]
    fields = ("case_id", "grievance_id", "parcel_id", "survey_number", "village", "taluka", "case_status", "review_stage", "opened_at", "updated_at", "resolved_at", "closed_at", "requires_field_verification", "requires_more_information", "resolution_type", "latest_priority_score", "latest_priority_level", "storage_mode")
    return _csv_response("administrative_cases", fields, rows)
