"""Validated Phase 5 inspection storage with transparent in-memory fallback."""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..schemas.inspection import InspectionSubmission

MAX_PHOTOS = 3
MAX_FILE_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
UPLOAD_ROOT = (Path(__file__).resolve().parents[2] / "uploads" / "inspections").resolve()

_lock = Lock()
_records: dict[str, dict] = {}
_history: dict[str, list[str]] = defaultdict(list)
_evidence: dict[str, dict] = {}
_submissions: dict[str, str] = {}
_sequence = 0


def _is_expected_image(data: bytes, mime_type: str) -> bool:
    if mime_type == "image/jpeg":
        return data.startswith(b"\xff\xd8\xff")
    if mime_type == "image/png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if mime_type == "image/webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False


async def validate_photos(photos: list[UploadFile]) -> list[dict]:
    if len(photos) > MAX_PHOTOS:
        raise HTTPException(422, detail={"code": "too_many_photos", "message": "A maximum of 3 photos is allowed."})
    validated = []
    for photo in photos:
        original = Path(photo.filename or "").name
        suffix = Path(original).suffix.lower()
        expected_mime = ALLOWED_TYPES.get(suffix)
        if not expected_mime or photo.content_type != expected_mime:
            raise HTTPException(422, detail={"code": "invalid_photo_type", "message": "Only JPEG, PNG, and WEBP photos are allowed."})
        content = await photo.read(MAX_FILE_BYTES + 1)
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(413, detail={"code": "photo_too_large", "message": "Each photo must be 5 MB or smaller."})
        if not content or not _is_expected_image(content, expected_mime):
            raise HTTPException(422, detail={"code": "invalid_photo_content", "message": "The uploaded file does not match its declared image type."})
        validated.append({"original_name": original, "suffix": suffix, "mime_type": expected_mime, "content": content})
    return validated


def _public_record(record: dict) -> dict:
    return {key: value for key, value in record.items() if key not in {"submission_key"}}


def _persist_to_database(db: Session, record: dict, evidence: list[dict]) -> bool:
    try:
        db.execute(text("""
            INSERT INTO field_inspections (
              inspection_id, submission_key, parcel_id, inspection_status, inspection_outcome,
              inspection_date, started_at, completed_at, latitude, longitude, gps_accuracy_m,
              location_source, officer_display_name, officer_reference, observations, recommendation,
              priority_score_at_inspection, priority_level_at_inspection,
              satellite_change_percentage_at_inspection, requires_follow_up
            ) VALUES (
              :inspection_id, :submission_key, :parcel_id, :inspection_status, :inspection_outcome,
              :inspection_date, :started_at, :completed_at, :latitude, :longitude, :gps_accuracy_m,
              :location_source, :officer_display_name, :officer_reference, :observations, :recommendation,
              :priority_score_at_inspection, :priority_level_at_inspection,
              :satellite_change_percentage_at_inspection, :requires_follow_up
            ) ON CONFLICT (submission_key) DO NOTHING
        """), record)
        for item in evidence:
            db.execute(text("""
                INSERT INTO inspection_evidence (
                  evidence_id, inspection_id, evidence_type, file_name, file_path, mime_type,
                  file_size_bytes, caption, captured_at
                ) VALUES (
                  :evidence_id, :inspection_id, :evidence_type, :file_name, :file_path, :mime_type,
                  :file_size_bytes, :caption, :captured_at
                ) ON CONFLICT (inspection_id, evidence_id) DO NOTHING
            """), item)
        db.commit()
        return True
    except (SQLAlchemyError, AttributeError):
        if hasattr(db, "rollback"):
            db.rollback()
        return False


def create_inspection(*, parcel: dict, priority: dict, payload: InspectionSubmission, photos: list[dict], submission_key: str, db: Session) -> tuple[dict, bool]:
    global _sequence
    with _lock:
        existing_id = _submissions.get(submission_key)
        if existing_id:
            return _public_record(_records[existing_id]), True
        now = datetime.now(timezone.utc)
        while True:
            _sequence += 1
            inspection_id = f"INSP-{now.year}-{_sequence:04d}"
            inspection_dir = (UPLOAD_ROOT / inspection_id).resolve()
            if inspection_id not in _records and not inspection_dir.exists():
                break
        if UPLOAD_ROOT not in inspection_dir.parents:
            raise HTTPException(400, detail={"code": "unsafe_path", "message": "Invalid inspection storage path."})
        inspection_dir.mkdir(parents=True, exist_ok=False)
        saved = []
        try:
            for item in photos:
                evidence_id = f"EVD-{uuid4().hex}"
                safe_name = f"{uuid4().hex}{item['suffix']}"
                target = (inspection_dir / safe_name).resolve()
                if inspection_dir not in target.parents:
                    raise HTTPException(400, detail={"code": "unsafe_path", "message": "Invalid evidence path."})
                target.write_bytes(item["content"])
                metadata = {
                    "evidence_id": evidence_id, "inspection_id": inspection_id, "evidence_type": "Photo",
                    "file_name": item["original_name"], "file_path": str(target), "mime_type": item["mime_type"],
                    "file_size_bytes": len(item["content"]), "caption": None, "captured_at": now,
                    "url": f"/api/inspections/{inspection_id}/evidence/{evidence_id}",
                }
                saved.append(metadata)
        except Exception:
            for item in saved:
                Path(item["file_path"]).unlink(missing_ok=True)
            inspection_dir.rmdir()
            raise

        values = payload.model_dump()
        record = {
            "inspection_id": inspection_id, "submission_key": submission_key, "parcel_id": parcel["parcel_id"],
            "inspection_status": "Inspection Completed", "inspection_date": now, "started_at": now,
            "completed_at": now, **values, "priority_score_at_inspection": priority["priority_score"],
            "priority_level_at_inspection": priority["priority_level"],
            "satellite_change_percentage_at_inspection": priority["change_percentage"],
            "location": {"latitude": values["latitude"], "longitude": values["longitude"], "accuracy_m": values["gps_accuracy_m"]} if values["latitude"] is not None else None,
            "evidence": [{key: value for key, value in item.items() if key not in {"file_path", "captured_at"}} for item in saved],
            "evidence_count": len(saved), "created_at": now, "updated_at": now,
            "message": "Inspection completed successfully",
        }
        database_saved = _persist_to_database(db, record, saved)
        record["storage_mode"] = "database" if database_saved else "fallback"
        record["storage_notice"] = "Inspection stored in PostgreSQL." if database_saved else "Demo inspection stored in local fallback mode — database unavailable. It will be lost when the backend restarts."
        _records[inspection_id] = record
        _history[parcel["parcel_id"]].append(inspection_id)
        for item in saved:
            _evidence[item["evidence_id"]] = item
        _submissions[submission_key] = inspection_id
        return _public_record(record), False


def inspection_history(parcel_id: str) -> list[dict]:
    with _lock:
        return [_public_record(_records[item]) for item in reversed(_history.get(parcel_id, []))]


def inspection_detail(inspection_id: str) -> dict | None:
    with _lock:
        record = _records.get(inspection_id)
        return _public_record(record) if record else None


def evidence_detail(inspection_id: str, evidence_id: str) -> dict | None:
    with _lock:
        item = _evidence.get(evidence_id)
        return item if item and item["inspection_id"] == inspection_id else None


def reset_fallback_store() -> None:
    global _sequence
    with _lock:
        _records.clear(); _history.clear(); _evidence.clear(); _submissions.clear(); _sequence = 0
