import re
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.case import CaseAction, CaseNote
from ..services.cases import (
    CASE_STATUSES, REVIEW_STAGES, add_review_note, case_context, case_queue,
    create_case, get_case_events, perform_action,
)
from ..services.grievances import grievance_detail

router = APIRouter(prefix="/api", tags=["administrative cases"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _key(value: str | None) -> str:
    if not value or not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", value):
        raise HTTPException(422, detail={"code": "invalid_action_key", "message": "A valid X-Idempotency-Key header is required."})
    return value


@router.post("/grievances/{grievance_id}/case")
def open_case(
    grievance_id: str,
    db: DatabaseSession,
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
) -> dict:
    grievance = grievance_detail(grievance_id, include_case=False)
    if grievance is None:
        raise HTTPException(404, detail={"code": "grievance_not_found", "message": "No grievance found for this reference."})
    record, existing = create_case(grievance=grievance, submission_key=_key(idempotency_key), db=db)
    return {**record, "case_already_exists": existing, "message": "Administrative case already exists." if existing else "Administrative case opened successfully."}


@router.get("/cases")
def list_cases(
    status: str | None = None,
    stage: str | None = None,
    taluka: str | None = None,
    priority_level: str | None = None,
    parcel_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=100),
) -> dict:
    items = case_queue(status=status, stage=stage, taluka=taluka, priority_level=priority_level, parcel_id=parcel_id, limit=limit)
    summary = {case_status: sum(item["case_status"] == case_status for item in items) for case_status in CASE_STATUSES}
    return {"type": "AdministrativeCaseQueue", "count": len(items), "items": items, "summary": summary, "storage_mode": "current-session fallback"}


@router.get("/cases/{case_id}")
def get_case_detail(case_id: str) -> dict:
    result = case_context(case_id)
    if result is None:
        raise HTTPException(404, detail={"code": "case_not_found", "message": "Administrative case was not found."})
    return result


@router.get("/cases/{case_id}/events")
def case_events(case_id: str) -> dict:
    result = case_context(case_id)
    if result is None:
        raise HTTPException(404, detail={"code": "case_not_found", "message": "Administrative case was not found."})
    items = get_case_events(case_id)
    return {"case_id": case_id.upper(), "count": len(items), "items": items}


@router.post("/cases/{case_id}/actions")
def case_action(
    case_id: str,
    payload: CaseAction,
    db: DatabaseSession,
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
) -> dict:
    record, duplicate = perform_action(case_id=case_id, action=payload, action_key=_key(idempotency_key), db=db)
    return {**record, "duplicate_action": duplicate, "message": "Administrative action recorded successfully."}


@router.post("/cases/{case_id}/notes")
def case_note(
    case_id: str,
    payload: CaseNote,
    db: DatabaseSession,
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
) -> dict:
    record, duplicate = add_review_note(case_id=case_id, note=payload.review_note, action_key=_key(idempotency_key), db=db)
    return {**record, "duplicate_action": duplicate, "message": "Administrative review note recorded successfully."}


@router.get("/case-options", include_in_schema=False)
def case_options() -> dict:
    return {"statuses": CASE_STATUSES, "review_stages": REVIEW_STAGES}
