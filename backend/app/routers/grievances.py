import json
import re
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..data import PARCELS
from ..database import get_db
from ..schemas.grievance import GrievanceSubmission
from ..services.grievances import create_grievance, evidence_detail, grievance_detail, grievance_history, grievance_queue
from ..services.inspections import validate_photos

router = APIRouter(prefix="/api", tags=["citizen grievances"])
DatabaseSession = Annotated[Session, Depends(get_db)]
PARCEL_INDEX = {feature["properties"]["parcel_id"]: feature["properties"] for feature in PARCELS["features"]}


def _parcel_or_404(parcel_id: str) -> dict:
    parcel = PARCEL_INDEX.get(parcel_id)
    if parcel is None:
        raise HTTPException(404, detail={"code": "parcel_not_found", "message": f"Parcel '{parcel_id}' was not found."})
    return parcel


@router.post("/parcels/{parcel_id}/grievances")
async def submit_grievance(
    parcel_id: str,
    db: DatabaseSession,
    payload: Annotated[str, Form()],
    photos: Annotated[list[UploadFile], File()] = [],
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
) -> dict:
    parcel = _parcel_or_404(parcel_id)
    if not idempotency_key or not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", idempotency_key):
        raise HTTPException(422, detail={"code": "invalid_submission_key", "message": "A valid X-Idempotency-Key header is required."})
    try:
        submission = GrievanceSubmission.model_validate(json.loads(payload))
    except (json.JSONDecodeError, ValidationError) as error:
        details = error.errors(include_context=False, include_input=False, include_url=False) if isinstance(error, ValidationError) else [{"msg": "Payload must be valid JSON"}]
        raise HTTPException(422, detail={"code": "invalid_grievance", "message": "Grievance validation failed.", "errors": details}) from error
    record, duplicate = create_grievance(
        parcel=parcel, payload=submission, photos=await validate_photos(photos),
        submission_key=idempotency_key, db=db,
    )
    record["duplicate_submission"] = duplicate
    return record


@router.get("/parcels/{parcel_id}/grievances")
def parcel_grievances(parcel_id: str) -> dict:
    _parcel_or_404(parcel_id)
    items = grievance_history(parcel_id)
    return {"parcel_id": parcel_id, "count": len(items), "items": items, "storage_mode": "current-session fallback"}


@router.get("/grievances/{grievance_id}")
def get_grievance(grievance_id: str) -> dict:
    item = grievance_detail(grievance_id)
    if item is None:
        raise HTTPException(404, detail={"code": "grievance_not_found", "message": "No grievance found for this reference."})
    return item


@router.get("/grievances")
def list_grievances(
    status: str | None = None,
    category: str | None = None,
    parcel_id: str | None = None,
    taluka: str | None = None,
    limit: int = Query(default=100, ge=1, le=100),
) -> dict:
    items = grievance_queue(status=status, category=category, parcel_id=parcel_id, taluka=taluka, limit=limit)
    return {"type": "GrievanceQueue", "count": len(items), "items": items, "storage_mode": "current-session fallback"}


@router.get("/grievances/{grievance_id}/evidence/{evidence_id}", include_in_schema=False)
def get_grievance_evidence(grievance_id: str, evidence_id: str) -> FileResponse:
    item = evidence_detail(grievance_id, evidence_id)
    if item is None:
        raise HTTPException(404, detail={"code": "evidence_not_found", "message": "Grievance evidence was not found."})
    return FileResponse(item["file_path"], media_type=item["mime_type"], filename=item["file_name"], content_disposition_type="inline")
