"""Deterministic Phase 7 administrative workflow with an explicit fallback store."""
from collections import defaultdict
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..data import PARCELS
from ..schemas.case import CaseAction
from .inspections import inspection_history
from .imagery import DEMO_IMAGERY
from .priority_engine import calculate_priority, phase3_change_result

ACTOR_DISPLAY = "Admin Officer"
ACTOR_REFERENCE = "DEMO-ADMIN-01"
CASE_STATUSES = (
    "Open", "Under Review", "Field Verification Requested",
    "More Information Required", "Ready for Decision", "Resolved", "Closed",
)
REVIEW_STAGES = (
    "Intake", "Initial Review", "Evidence Review", "Field Verification",
    "Decision Review", "Finalized",
)
GRIEVANCE_STATUS_BY_CASE = {
    "Open": "Under Review",
    "Under Review": "Under Review",
    "Field Verification Requested": "Field Verification Recommended",
    "More Information Required": "More Information Required",
    "Ready for Decision": "Under Review",
    "Resolved": "Resolved",
    "Closed": "Closed",
}

_lock = RLock()
_cases: dict[str, dict] = {}
_by_grievance: dict[str, str] = {}
_events: dict[str, list[dict]] = defaultdict(list)
_requests: dict[tuple[str, str], dict] = {}
_sequence = 0
PARCEL_INDEX = {feature["properties"]["parcel_id"]: feature["properties"] for feature in PARCELS["features"]}


def _database_write(db: Session, statements: list[tuple[str, dict]]) -> bool:
    try:
        for statement, params in statements:
            db.execute(text(statement), params)
        db.commit()
        return True
    except (SQLAlchemyError, AttributeError):
        if hasattr(db, "rollback"):
            db.rollback()
        return False


def _case_statement(record: dict) -> tuple[str, dict]:
    return ("""
        INSERT INTO administrative_cases (
          case_id, grievance_id, parcel_id, case_status, review_stage,
          assigned_officer_display, assigned_officer_reference, opened_at, updated_at,
          resolved_at, closed_at, requires_field_verification, requires_more_information,
          administrative_summary, resolution_type, resolution_note, latest_priority_score,
          latest_priority_level, storage_mode, created_at
        ) VALUES (
          :case_id, :grievance_id, :parcel_id, :case_status, :review_stage,
          :assigned_officer_display, :assigned_officer_reference, :opened_at, :updated_at,
          :resolved_at, :closed_at, :requires_field_verification, :requires_more_information,
          :administrative_summary, :resolution_type, :resolution_note, :latest_priority_score,
          :latest_priority_level, 'database', :created_at
        ) ON CONFLICT (case_id) DO UPDATE SET
          case_status = EXCLUDED.case_status, review_stage = EXCLUDED.review_stage,
          updated_at = EXCLUDED.updated_at, resolved_at = EXCLUDED.resolved_at,
          closed_at = EXCLUDED.closed_at,
          requires_field_verification = EXCLUDED.requires_field_verification,
          requires_more_information = EXCLUDED.requires_more_information,
          administrative_summary = EXCLUDED.administrative_summary,
          resolution_type = EXCLUDED.resolution_type, resolution_note = EXCLUDED.resolution_note,
          latest_priority_score = EXCLUDED.latest_priority_score,
          latest_priority_level = EXCLUDED.latest_priority_level
    """, record)


def _event_statement(event: dict) -> tuple[str, dict]:
    return ("""
        INSERT INTO administrative_case_events (
          event_id, action_key, case_id, event_type, from_status, to_status,
          from_stage, to_stage, note, actor_display, actor_reference, created_at
        ) VALUES (
          :event_id, :action_key, :case_id, :event_type, :from_status, :to_status,
          :from_stage, :to_stage, :note, :actor_display, :actor_reference, :created_at
        ) ON CONFLICT (action_key) DO NOTHING
    """, event)


def _new_event(*, case: dict, event_type: str, note: str, action_key: str,
               from_status: str | None = None, from_stage: str | None = None) -> dict:
    return {
        "event_id": f"CASE-EVT-{uuid4().hex}", "action_key": action_key,
        "case_id": case["case_id"], "event_type": event_type,
        "from_status": from_status, "to_status": case["case_status"],
        "from_stage": from_stage, "to_stage": case["review_stage"],
        "note": note, "actor_display": ACTOR_DISPLAY,
        "actor_reference": ACTOR_REFERENCE, "created_at": datetime.now(timezone.utc),
    }


def _public_case(record: dict) -> dict:
    return dict(record)


def citizen_case_for_grievance(grievance_id: str) -> dict | None:
    with _lock:
        case_id = _by_grievance.get(grievance_id.upper())
        if not case_id:
            return None
        record = _cases[case_id]
        result = {
            "case_id": record["case_id"], "case_status": record["case_status"],
            "review_stage": record["review_stage"], "updated_at": record["updated_at"],
        }
        if record["case_status"] in {"Resolved", "Closed"}:
            result["resolution_type"] = record["resolution_type"]
        return result


def create_case(*, grievance: dict, submission_key: str, db: Session) -> tuple[dict, bool]:
    global _sequence
    with _lock:
        existing = _by_grievance.get(grievance["grievance_id"])
        if existing:
            return _public_case(_cases[existing]), True
        request_key = ("create", submission_key)
        if request_key in _requests:
            return dict(_requests[request_key]), True
        _sequence += 1
        now = datetime.now(timezone.utc)
        case_id = f"CASE-{now.year}-{_sequence:04d}"
        priority = calculate_priority(PARCEL_INDEX[grievance["parcel_id"]])
        record = {
            "case_id": case_id, "grievance_id": grievance["grievance_id"],
            "parcel_id": grievance["parcel_id"], "survey_number": grievance["survey_number"],
            "village": grievance["village"], "taluka": grievance["taluka"],
            "case_status": "Open", "review_stage": "Intake",
            "assigned_officer_display": ACTOR_DISPLAY,
            "assigned_officer_reference": ACTOR_REFERENCE,
            "opened_at": now, "updated_at": now, "resolved_at": None, "closed_at": None,
            "requires_field_verification": False, "requires_more_information": False,
            "administrative_summary": None, "resolution_type": None, "resolution_note": None,
            "latest_priority_score": priority["priority_score"],
            "latest_priority_level": priority["priority_level"],
            "created_at": now,
        }
        event = _new_event(
            case=record, event_type="Case Created",
            note="Administrative case opened from citizen grievance.",
            action_key=f"create:{submission_key}",
        )
        stored = _database_write(db, [_case_statement(record), _event_statement(event)])
        record["storage_mode"] = "database" if stored else "fallback"
        record["storage_notice"] = "Administrative case stored in PostgreSQL." if stored else "Administrative case stored in local fallback mode — database unavailable. It will be lost when the backend restarts."
        _cases[case_id] = record
        _by_grievance[grievance["grievance_id"]] = case_id
        _events[case_id].append(event)
        _requests[request_key] = _public_case(record)
        from .grievances import update_grievance_status
        update_grievance_status(grievance["grievance_id"], GRIEVANCE_STATUS_BY_CASE["Open"], now, db)
        return _public_case(record), False


def case_queue(*, status: str | None = None, stage: str | None = None,
               taluka: str | None = None, priority_level: str | None = None,
               parcel_id: str | None = None,
               limit: int = 100) -> list[dict]:
    with _lock:
        items = [_public_case(item) for item in _cases.values()]
    if status:
        items = [item for item in items if item["case_status"].lower() == status.lower()]
    if stage:
        items = [item for item in items if item["review_stage"].lower() == stage.lower()]
    if taluka:
        items = [item for item in items if item["taluka"].lower() == taluka.lower()]
    if priority_level:
        items = [item for item in items if item["latest_priority_level"].lower() == priority_level.lower()]
    if parcel_id:
        items = [item for item in items if item["parcel_id"].lower() == parcel_id.lower()]
    return sorted(items, key=lambda item: (item["updated_at"], item["case_id"]), reverse=True)[:limit]


def get_case(case_id: str) -> dict | None:
    with _lock:
        record = _cases.get(case_id.upper())
        return _public_case(record) if record else None


def get_case_events(case_id: str) -> list[dict]:
    with _lock:
        return [dict(item) for item in _events.get(case_id.upper(), [])]


def case_context(case_id: str) -> dict | None:
    record = get_case(case_id)
    if record is None:
        return None
    from .grievances import grievance_detail
    grievance = grievance_detail(record["grievance_id"], include_case=False)
    parcel = PARCEL_INDEX[record["parcel_id"]]
    priority = calculate_priority(parcel)
    change = phase3_change_result(record["parcel_id"])
    public_change = None
    if change:
        imagery = DEMO_IMAGERY[record["parcel_id"]]
        relative = f"{record['parcel_id']}/{imagery[0]['capture_date']}_{imagery[-1]['capture_date']}"
        public_change = {
            key: value for key, value in change.items() if key not in {"mask_path", "overlay_path"}
        }
        public_change.update({
            "before_date": imagery[0]["capture_date"], "after_date": imagery[-1]["capture_date"],
            "mask_url": f"/generated/{relative}/change-mask.png",
            "overlay_url": f"/generated/{relative}/change-overlay.png",
            "legal_notice": "Automated change detection is indicative only and does not constitute a legal determination.",
        })
    inspections = inspection_history(record["parcel_id"])
    return {
        **record, "grievance": grievance, "parcel": parcel, "priority": priority,
        "satellite_analysis": public_change, "inspections": inspections,
        "inspection_count": len(inspections),
        "grievance_evidence_count": grievance["evidence_count"],
        "inspection_evidence_count": sum(item["evidence_count"] for item in inspections),
        "events": get_case_events(case_id),
        "allowed_actions": allowed_actions(record),
        "demo_session": {"actor_display": ACTOR_DISPLAY, "actor_reference": ACTOR_REFERENCE},
    }


def allowed_actions(case: dict) -> list[str]:
    status = case["case_status"]
    if status in {"Open", "Field Verification Requested", "More Information Required"}:
        return ["start_review"]
    if status == "Under Review":
        return ["request_field_verification", "request_more_information", "mark_ready_for_decision"]
    if status == "Ready for Decision":
        return ["resolve_case"]
    if status == "Resolved":
        return ["close_case"]
    return []


def _transition(case: dict, action: CaseAction) -> tuple[str, str, str]:
    current = case["case_status"]
    if action.action not in allowed_actions(case):
        raise HTTPException(400, detail={"code": "invalid_transition", "message": f"Action '{action.action}' is not allowed while the case is {current}."})
    if action.action == "start_review":
        return "Under Review", "Initial Review" if current == "Open" else "Evidence Review", "Review Started"
    if action.action == "request_field_verification":
        return "Field Verification Requested", "Field Verification", "Field Verification Requested"
    if action.action == "request_more_information":
        return "More Information Required", "Evidence Review", "More Information Requested"
    if action.action == "mark_ready_for_decision":
        if case["requires_field_verification"] and not inspection_history(case["parcel_id"]):
            raise HTTPException(400, detail={"code": "field_verification_incomplete", "message": "A completed field inspection is required before decision review."})
        if not any(item["event_type"] in {"Review Started", "Review Note Added"} for item in _events[case["case_id"]]):
            raise HTTPException(400, detail={"code": "review_required", "message": "Start the administrative review before marking the case ready for decision."})
        return "Ready for Decision", "Decision Review", "Ready for Decision"
    if action.action == "resolve_case":
        return "Resolved", "Finalized", "Case Resolved"
    return "Closed", "Finalized", "Case Closed"


def perform_action(*, case_id: str, action: CaseAction, action_key: str, db: Session) -> tuple[dict, bool]:
    with _lock:
        request_key = (case_id.upper(), action_key)
        if request_key in _requests:
            return dict(_requests[request_key]), True
        case = _cases.get(case_id.upper())
        if case is None:
            raise HTTPException(404, detail={"code": "case_not_found", "message": "Administrative case was not found."})
        old_status, old_stage = case["case_status"], case["review_stage"]
        new_status, new_stage, event_type = _transition(case, action)
        now = datetime.now(timezone.utc)
        case["case_status"], case["review_stage"], case["updated_at"] = new_status, new_stage, now
        case["requires_field_verification"] = new_status == "Field Verification Requested" or (case["requires_field_verification"] and new_status not in {"Resolved", "Closed"})
        case["requires_more_information"] = new_status == "More Information Required"
        case["administrative_summary"] = action.note
        if new_status == "Resolved":
            case["resolution_type"], case["resolution_note"], case["resolved_at"] = action.resolution_type, action.note, now
        if new_status == "Closed":
            case["closed_at"] = now
        event = _new_event(
            case=case, event_type=event_type, note=action.note,
            action_key=f"action:{case_id}:{action_key}",
            from_status=old_status, from_stage=old_stage,
        )
        stored = _database_write(db, [_case_statement(case), _event_statement(event)])
        case["storage_mode"] = "database" if stored else "fallback"
        case["storage_notice"] = "Administrative case stored in PostgreSQL." if stored else "Administrative case stored in local fallback mode — database unavailable. It will be lost when the backend restarts."
        _events[case["case_id"]].append(event)
        result = _public_case(case)
        _requests[request_key] = result
        from .grievances import update_grievance_status
        update_grievance_status(case["grievance_id"], GRIEVANCE_STATUS_BY_CASE[new_status], now, db, case["resolution_type"])
        return result, False


def add_review_note(*, case_id: str, note: str, action_key: str, db: Session) -> tuple[dict, bool]:
    with _lock:
        request_key = (case_id.upper(), action_key)
        if request_key in _requests:
            return dict(_requests[request_key]), True
        case = _cases.get(case_id.upper())
        if case is None:
            raise HTTPException(404, detail={"code": "case_not_found", "message": "Administrative case was not found."})
        if case["case_status"] == "Closed":
            raise HTTPException(400, detail={"code": "case_closed", "message": "Closed cases are read-only."})
        now = datetime.now(timezone.utc)
        case["updated_at"], case["administrative_summary"] = now, note
        event = _new_event(
            case=case, event_type="Review Note Added", note=note,
            action_key=f"note:{case_id}:{action_key}",
            from_status=case["case_status"], from_stage=case["review_stage"],
        )
        stored = _database_write(db, [_case_statement(case), _event_statement(event)])
        case["storage_mode"] = "database" if stored else "fallback"
        case["storage_notice"] = "Administrative case stored in PostgreSQL." if stored else "Administrative case stored in local fallback mode — database unavailable. It will be lost when the backend restarts."
        _events[case["case_id"]].append(event)
        result = _public_case(case)
        _requests[request_key] = result
        return result, False


def reset_fallback_store() -> None:
    global _sequence
    with _lock:
        _cases.clear(); _by_grievance.clear(); _events.clear(); _requests.clear(); _sequence = 0
