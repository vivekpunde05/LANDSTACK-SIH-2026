import json
import re
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..data import PARCELS
from ..database import get_db
from ..schemas.inspection import InspectionSubmission
from ..services.inspections import create_inspection, evidence_detail, inspection_detail, inspection_history, validate_photos
from ..services.priority_engine import calculate_priority

router = APIRouter(prefix="/api", tags=["field inspections"])
DatabaseSession = Annotated[Session, Depends(get_db)]
PARCEL_INDEX = {feature["properties"]["parcel_id"]: feature["properties"] for feature in PARCELS["features"]}


def _parcel_or_404(parcel_id: str) -> dict:
    parcel = PARCEL_INDEX.get(parcel_id)
    if parcel is None:
        raise HTTPException(404, detail={"code": "parcel_not_found", "message": f"Parcel '{parcel_id}' was not found."})
    return parcel


@router.post("/parcels/{parcel_id}/inspections")
async def submit_inspection(
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
        submission = InspectionSubmission.model_validate(json.loads(payload))
    except (json.JSONDecodeError, ValidationError) as error:
        details = error.errors(include_context=False, include_input=False, include_url=False) if isinstance(error, ValidationError) else [{"msg": "Payload must be valid JSON"}]
        raise HTTPException(422, detail={"code": "invalid_inspection", "message": "Inspection validation failed.", "errors": details}) from error
    record, duplicate = create_inspection(
        parcel=parcel,
        priority=calculate_priority(parcel),
        payload=submission,
        photos=await validate_photos(photos),
        submission_key=idempotency_key,
        db=db,
    )
    record["duplicate_submission"] = duplicate
    return record


@router.get("/parcels/{parcel_id}/inspections")
def parcel_inspections(parcel_id: str) -> dict:
    _parcel_or_404(parcel_id)
    items = inspection_history(parcel_id)
    return {"parcel_id": parcel_id, "count": len(items), "items": items, "storage_mode": "current-session fallback"}


@router.get("/inspections/{inspection_id}")
def get_inspection(inspection_id: str) -> dict:
    record = inspection_detail(inspection_id)
    if record is None:
        raise HTTPException(404, detail={"code": "inspection_not_found", "message": "Inspection was not found in the current session."})
    return record


@router.get("/inspections/{inspection_id}/evidence/{evidence_id}", include_in_schema=False)
def get_evidence(inspection_id: str, evidence_id: str) -> FileResponse:
    item = evidence_detail(inspection_id, evidence_id)
    if item is None:
        raise HTTPException(404, detail={"code": "evidence_not_found", "message": "Evidence photo was not found."})
    return FileResponse(item["file_path"], media_type=item["mime_type"], filename=item["file_name"], content_disposition_type="inline")
