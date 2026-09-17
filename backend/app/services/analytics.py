"""Descriptive Phase 8 analytics derived from existing LANDSTACK sources."""
from collections import Counter
from datetime import datetime, timezone

from ..data import PARCELS
from .cases import CASE_STATUSES, case_queue
from .grievances import grievance_queue
from .imagery import DEMO_IMAGERY
from .inspections import inspection_history
from .priority_engine import PRIORITY_THRESHOLDS, phase3_change_result, rank_priorities

PRIORITY_LEVELS = tuple(label for _minimum, label in reversed(PRIORITY_THRESHOLDS))
VERIFICATION_STATUSES = ("Verified", "Pending Verification", "Requires Verification")
GRIEVANCE_CATEGORIES = (
    "Land Record Correction Request", "Boundary / Parcel Concern",
    "Suspected Land-Use Change", "Access / Right-of-Way Concern",
    "Public Land Concern", "Record Information Request", "Other",
)
GRIEVANCE_STATUSES = (
    "Submitted", "Under Review", "Field Verification Recommended",
    "More Information Required", "Resolved", "Closed",
)
INSPECTION_OUTCOMES = (
    "No Significant Issue Observed", "Requires Further Review",
    "Change Confirmed On Site", "Unable To Verify",
)
SATELLITE_STATUSES = (
    "No significant change detected", "Potential change", "Requires verification",
)
ACTIVE_GRIEVANCE_STATUSES = set(GRIEVANCE_STATUSES) - {"Resolved", "Closed"}
ACTIVE_CASE_STATUSES = set(CASE_STATUSES) - {"Resolved", "Closed"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def analytics_snapshot() -> dict:
    parcels = [feature["properties"] for feature in PARCELS["features"]]
    priorities = rank_priorities(limit=100)
    grievances = grievance_queue(limit=100)
    cases = case_queue(limit=100)
    inspections = [item for parcel in parcels for item in inspection_history(parcel["parcel_id"])]
    analyses = [phase3_change_result(parcel_id) for parcel_id in DEMO_IMAGERY]
    analyses = [item for item in analyses if item is not None]
    return {
        "parcels": parcels, "priorities": priorities, "analyses": analyses,
        "inspections": inspections, "grievances": grievances, "cases": cases,
        "storage_mode": "fallback", "refreshed_at": _now(),
    }


def analytics_summary(snapshot: dict | None = None) -> dict:
    data = snapshot or analytics_snapshot()
    priorities, inspections = data["priorities"], data["inspections"]
    grievances, cases = data["grievances"], data["cases"]
    resolved_cases = sum(item["case_status"] in {"Resolved", "Closed"} for item in cases)
    return {
        "total_parcels": len(data["parcels"]),
        "review_recommended_parcels": sum(item["priority_level"] != "Routine" for item in priorities),
        "satellite_analyses": len(data["analyses"]),
        "completed_inspections": sum(item["inspection_status"] == "Inspection Completed" for item in inspections),
        "open_grievances": sum(item["status"] in ACTIVE_GRIEVANCE_STATUSES for item in grievances),
        "active_cases": sum(item["case_status"] in ACTIVE_CASE_STATUSES for item in cases),
        "resolved_or_closed_cases": resolved_cases,
        "total_grievances": len(grievances), "total_inspections": len(inspections),
        "total_cases": len(cases),
        "resolution_rate": round(resolved_cases / len(cases) * 100, 1) if cases else None,
        "requires_follow_up_inspections": sum(bool(item["requires_follow_up"]) for item in inspections),
        "storage_mode": data["storage_mode"], "refreshed_at": data["refreshed_at"],
        "data_notice": "Analytics reflect current local demo-session data.",
    }


def _distribution(items: list[dict], key: str, labels: tuple[str, ...]) -> list[dict]:
    counts = Counter(item.get(key) for item in items)
    total = len(items)
    return [
        {"label": label, "count": counts[label], "percentage": round(counts[label] / total * 100, 1) if total else 0.0}
        for label in labels
    ]


def analytics_distributions(snapshot: dict | None = None) -> dict:
    data = snapshot or analytics_snapshot()
    analyses = data["analyses"]
    return {
        "priority_levels": _distribution(data["priorities"], "priority_level", PRIORITY_LEVELS),
        "verification_statuses": _distribution(data["parcels"], "verification_status", VERIFICATION_STATUSES),
        "grievance_categories": _distribution(data["grievances"], "category", GRIEVANCE_CATEGORIES),
        "grievance_statuses": _distribution(data["grievances"], "status", GRIEVANCE_STATUSES),
        "case_statuses": _distribution(data["cases"], "case_status", CASE_STATUSES),
        "inspection_outcomes": _distribution(data["inspections"], "inspection_outcome", INSPECTION_OUTCOMES),
        "satellite_statuses": _distribution(analyses, "change_status", SATELLITE_STATUSES),
        "average_satellite_change_percentage": round(sum(float(item["change_percentage"]) for item in analyses) / len(analyses), 2) if analyses else None,
        "storage_mode": data["storage_mode"], "refreshed_at": data["refreshed_at"],
    }


def analytics_geography(snapshot: dict | None = None) -> dict:
    data = snapshot or analytics_snapshot()
    rows = []
    for taluka in sorted({item["taluka"] for item in data["parcels"]}):
        parcels = [item for item in data["parcels"] if item["taluka"] == taluka]
        parcel_ids = {item["parcel_id"] for item in parcels}
        priorities = [item for item in data["priorities"] if item["parcel_id"] in parcel_ids]
        grievances = [item for item in data["grievances"] if item["parcel_id"] in parcel_ids]
        inspections = [item for item in data["inspections"] if item["parcel_id"] in parcel_ids]
        cases = [item for item in data["cases"] if item["parcel_id"] in parcel_ids]
        rows.append({
            "taluka": taluka, "parcel_count": len(parcels),
            "review_count": sum(item["priority_level"] != "Routine" for item in priorities),
            "grievance_count": len(grievances), "inspection_count": len(inspections),
            "active_case_count": sum(item["case_status"] in ACTIVE_CASE_STATUSES for item in cases),
        })
    rows.sort(key=lambda item: (-(item["grievance_count"] + item["inspection_count"] + item["active_case_count"]), -item["parcel_count"], item["taluka"]))
    villages = []
    for village in sorted({item["village"] for item in data["parcels"]}):
        parcels = [item for item in data["parcels"] if item["village"] == village]
        parcel_ids = {item["parcel_id"] for item in parcels}
        villages.append({
            "village": village, "taluka": parcels[0]["taluka"], "parcel_count": len(parcels),
            "review_count": sum(item["priority_level"] != "Routine" for item in data["priorities"] if item["parcel_id"] in parcel_ids),
            "grievance_count": sum(item["parcel_id"] in parcel_ids for item in data["grievances"]),
            "inspection_count": sum(item["parcel_id"] in parcel_ids for item in data["inspections"]),
            "active_case_count": sum(item["parcel_id"] in parcel_ids and item["case_status"] in ACTIVE_CASE_STATUSES for item in data["cases"]),
        })
    return {"talukas": rows, "villages": villages, "sort": "workflow activity, then parcel count", "storage_mode": data["storage_mode"], "refreshed_at": data["refreshed_at"]}


def analytics_attention(snapshot: dict | None = None, limit: int = 20) -> dict:
    data = snapshot or analytics_snapshot()
    items = []
    for item in data["priorities"]:
        if item["priority_level"] in {"High Priority Review", "Urgent Review"}:
            items.append({"type": "Parcel priority", "reference": item["parcel_id"], "parcel_id": item["parcel_id"], "taluka": item["taluka"], "status": item["priority_level"], "reason": f"Inspection Priority Score {item['priority_score']} / 100", "action": "priority", "sort_score": 300 + item["priority_score"]})
    for item in data["cases"]:
        if item["case_status"] in ACTIVE_CASE_STATUSES:
            items.append({"type": "Administrative case", "reference": item["case_id"], "parcel_id": item["parcel_id"], "taluka": item["taluka"], "status": item["case_status"], "reason": f"Administrative case is at {item['review_stage']} stage", "action": "case", "sort_score": 500 if item["case_status"] in {"Field Verification Requested", "More Information Required"} else 400})
    for item in data["grievances"]:
        if item["status"] in ACTIVE_GRIEVANCE_STATUSES and not item.get("administrative_case"):
            items.append({"type": "Grievance", "reference": item["grievance_id"], "parcel_id": item["parcel_id"], "taluka": item["taluka"], "status": item["status"], "reason": "Citizen report awaits administrative case review", "action": "grievance", "sort_score": 350})
    items.sort(key=lambda item: (-item.pop("sort_score"), item["reference"]))
    return {"count": min(len(items), limit), "items": items[:limit], "storage_mode": data["storage_mode"], "refreshed_at": data["refreshed_at"]}
