"""Deterministic grievance workflow with explicit current-session fallback."""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..schemas.grievance import GrievanceSubmission

UPLOAD_ROOT = (Path(__file__).resolve().parents[2] / "uploads" / "grievances").resolve()
_lock = Lock()
_records: dict[str, dict] = {}
_history: dict[str, list[str]] = defaultdict(list)
_evidence: dict[str, dict] = {}
_submissions: dict[str, str] = {}
_sequence = 0


def _public(record: dict, include_case: bool = True) -> dict:
    result = {
        key: value for key, value in record.items()
        if key not in {"submission_key", "citizen_display_name", "contact_reference"}
    }
    if include_case:
        from .cases import citizen_case_for_grievance
        result["administrative_case"] = citizen_case_for_grievance(record["grievance_id"])
    return result


def _persist(db: Session, record: dict, evidence: list[dict]) -> bool:
    database_record = {**record, "storage_mode": "database"}
    try:
        db.execute(text("""
            INSERT INTO citizen_grievances (
              grievance_id, submission_key, parcel_id, category, custom_category, description,
              status, priority_reference, submitted_at, updated_at, requires_field_verification,
              resolution_note, storage_mode, citizen_display_name, contact_reference
            ) VALUES (
              :grievance_id, :submission_key, :parcel_id, :category, :custom_category, :description,
              :status, :priority_reference, :submitted_at, :updated_at, :requires_field_verification,
              :resolution_note, :storage_mode, :citizen_display_name, :contact_reference
            ) ON CONFLICT (submission_key) DO NOTHING
        """), database_record)
        for item in evidence:
            db.execute(text("""
                INSERT INTO grievance_evidence (
                  evidence_id, grievance_id, file_name, file_path, mime_type, file_size_bytes, caption
                ) VALUES (
                  :evidence_id, :grievance_id, :file_name, :file_path, :mime_type, :file_size_bytes, :caption
                ) ON CONFLICT (grievance_id, evidence_id) DO NOTHING
            """), item)
        db.commit()
        return True
    except (SQLAlchemyError, AttributeError):
        if hasattr(db, "rollback"):
            db.rollback()
        return False


def create_grievance(*, parcel: dict, payload: GrievanceSubmission, photos: list[dict], submission_key: str, db: Session) -> tuple[dict, bool]:
    global _sequence
    with _lock:
        existing_id = _submissions.get(submission_key)
        if existing_id:
            return _public(_records[existing_id]), True
        now = datetime.now(timezone.utc)
        while True:
            _sequence += 1
            grievance_id = f"GRV-{now.year}-{_sequence:04d}"
            grievance_dir = (UPLOAD_ROOT / grievance_id).resolve()
            if grievance_id not in _records and not grievance_dir.exists():
                break
        if UPLOAD_ROOT not in grievance_dir.parents:
            raise HTTPException(400, detail={"code": "unsafe_path", "message": "Invalid grievance storage path."})
        grievance_dir.mkdir(parents=True, exist_ok=False)
        saved = []
        try:
            for photo in photos:
                evidence_id = f"GEV-{uuid4().hex}"
                target = (grievance_dir / f"{uuid4().hex}{photo['suffix']}").resolve()
                if grievance_dir not in target.parents:
                    raise HTTPException(400, detail={"code": "unsafe_path", "message": "Invalid evidence path."})
                target.write_bytes(photo["content"])
                saved.append({
                    "evidence_id": evidence_id, "grievance_id": grievance_id,
                    "file_name": photo["original_name"], "file_path": str(target),
                    "mime_type": photo["mime_type"], "file_size_bytes": len(photo["content"]),
                    "caption": None, "url": f"/api/grievances/{grievance_id}/evidence/{evidence_id}",
                })
        except Exception:
            for item in saved:
                Path(item["file_path"]).unlink(missing_ok=True)
            grievance_dir.rmdir()
            raise

        values = payload.model_dump()
        record = {
            "grievance_id": grievance_id, "submission_key": submission_key,
            "parcel_id": parcel["parcel_id"], "survey_number": parcel["survey_number"],
            "village": parcel["village"], "taluka": parcel["taluka"], **values,
            "status": "Submitted", "priority_reference": "phase4-v1",
            "submitted_at": now, "updated_at": now, "requires_field_verification": False,
            "resolution_note": None,
            "evidence": [{key: value for key, value in item.items() if key != "file_path"} for item in saved],
            "evidence_count": len(saved), "message": "Grievance submitted successfully",
            "verification_notice": "Citizen-submitted information requires official verification and does not constitute a legal determination.",
        }
        stored = _persist(db, record, saved)
        record["storage_mode"] = "database" if stored else "fallback"
        record["storage_notice"] = "Grievance stored in PostgreSQL." if stored else "Demo grievance stored in local fallback mode — database unavailable. It will be lost when the backend restarts."
        _records[grievance_id] = record
        _history[parcel["parcel_id"]].append(grievance_id)
        for item in saved:
            _evidence[item["evidence_id"]] = item
        _submissions[submission_key] = grievance_id
        return _public(record), False


def grievance_history(parcel_id: str) -> list[dict]:
    with _lock:
        return [_public(_records[item]) for item in reversed(_history.get(parcel_id, []))]


def grievance_detail(grievance_id: str, include_case: bool = True) -> dict | None:
    with _lock:
        item = _records.get(grievance_id.upper())
        return _public(item, include_case=include_case) if item else None


def update_grievance_status(grievance_id: str, status: str, updated_at: datetime, db: Session, resolution_type: str | None = None) -> None:
    with _lock:
        record = _records.get(grievance_id)
        if record is not None:
            record["status"] = status
            record["updated_at"] = updated_at
            record["requires_field_verification"] = status == "Field Verification Recommended"
            if resolution_type:
                record["resolution_note"] = resolution_type
    try:
        db.execute(text("""
            UPDATE citizen_grievances
            SET status = :status, updated_at = :updated_at,
                requires_field_verification = :requires_field_verification,
                resolution_note = COALESCE(:resolution_type, resolution_note)
            WHERE grievance_id = :grievance_id
        """), {
            "status": status, "updated_at": updated_at,
            "requires_field_verification": status == "Field Verification Recommended",
            "resolution_type": resolution_type, "grievance_id": grievance_id,
        })
        db.commit()
    except (SQLAlchemyError, AttributeError):
        if hasattr(db, "rollback"):
            db.rollback()


def grievance_queue(*, status: str | None = None, category: str | None = None, parcel_id: str | None = None, taluka: str | None = None, limit: int = 100) -> list[dict]:
    with _lock:
        items = [_public(item) for item in _records.values()]
    if status:
        items = [item for item in items if item["status"].lower() == status.lower()]
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    if parcel_id:
        items = [item for item in items if item["parcel_id"].lower() == parcel_id.lower()]
    if taluka:
        items = [item for item in items if item["taluka"].lower() == taluka.lower()]
    return sorted(items, key=lambda item: (item["submitted_at"], item["grievance_id"]), reverse=True)[:limit]


def evidence_detail(grievance_id: str, evidence_id: str) -> dict | None:
    with _lock:
        item = _evidence.get(evidence_id)
        return item if item and item["grievance_id"] == grievance_id else None


def reset_fallback_store() -> None:
    global _sequence
    with _lock:
        _records.clear(); _history.clear(); _evidence.clear(); _submissions.clear(); _sequence = 0
