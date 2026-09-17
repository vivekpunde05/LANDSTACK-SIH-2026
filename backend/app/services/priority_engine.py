"""Deterministic, explainable workflow prioritization for synthetic parcels."""
from datetime import datetime, timezone
from functools import lru_cache

from ..data import PARCELS
from .change_detection import analyze_change
from .imagery import DATASET_ROOT, DEMO_IMAGERY, GENERATED_ROOT

SCORE_VERSION = "phase4-v1"
PRIORITY_WEIGHTS = {
    "satellite_change": 40,
    "verification_status": 20,
    "record_status": 15,
    "review_status": 15,
    "recency": 10,
}
PRIORITY_THRESHOLDS = (
    (75, "Urgent Review"),
    (50, "High Priority Review"),
    (25, "Review Recommended"),
    (0, "Routine"),
)


@lru_cache(maxsize=8)
def phase3_change_result(parcel_id: str) -> dict | None:
    items = DEMO_IMAGERY.get(parcel_id)
    if not items:
        return None
    parcel = next(feature for feature in PARCELS["features"] if feature["properties"]["parcel_id"] == parcel_id)
    return analyze_change(
        DATASET_ROOT / items[0]["image_path"],
        DATASET_ROOT / items[-1]["image_path"],
        GENERATED_ROOT / parcel_id / f'{items[0]["capture_date"]}_{items[-1]["capture_date"]}',
        float(parcel["properties"]["area_hectares"]),
    )


def _factor(name: str, points: int, key: str, reason: str) -> dict:
    return {"factor": name, "points": points, "max_points": PRIORITY_WEIGHTS[key], "reason": reason}


def _satellite_factor(change: dict | None) -> dict:
    if change is None:
        return _factor("Satellite change", 0, "satellite_change", "No satellite analysis is available; no points added")
    percentage = float(change["change_percentage"])
    points = 0 if percentage < 1.5 else 10 if percentage < 4 else 20 if percentage < 8 else 30 if percentage <= 15 else 40
    return _factor("Satellite change", points, "satellite_change", f"{percentage:.2f}% visual change detected by the demo analysis")


def _status_factor(label: str, value: str, key: str, mapping: dict[str, int]) -> dict:
    points = mapping.get(value, 0)
    return _factor(label, points, key, f"Current status: {value}")


def _recency_factor(change: dict | None) -> dict:
    if change is None:
        return _factor("Analysis recency", 0, "recency", "No dated satellite analysis is available")
    points = 10 if float(change["change_percentage"]) >= 1.5 else 3
    reason = "Recent 2026 demo analysis detected a meaningful visual change" if points == 10 else "Recent 2026 demo analysis found no significant change"
    return _factor("Analysis recency", points, "recency", reason)


def priority_level(score: int) -> str:
    return next(label for minimum, label in PRIORITY_THRESHOLDS if score >= minimum)


def calculate_priority(parcel: dict, calculated_at: str | None = None) -> dict:
    change = phase3_change_result(parcel["parcel_id"])
    factors = [
        _satellite_factor(change),
        _status_factor("Verification status", parcel["verification_status"], "verification_status", {"Verified": 0, "Pending Verification": 15, "Requires Verification": 20}),
        _status_factor("Record status", parcel["record_status"], "record_status", {"Active": 0, "Under Review": 15}),
        _status_factor("Existing review status", parcel["risk_status"], "review_status", {"Normal": 0, "Requires Verification": 8, "Flagged for Review": 15}),
        _recency_factor(change),
    ]
    score = max(0, min(100, sum(item["points"] for item in factors)))
    level = priority_level(score)
    recommendations = {
        "Routine": "Continue routine monitoring",
        "Review Recommended": "Review available records before scheduling an inspection",
        "High Priority Review": "Prioritize for field verification",
        "Urgent Review": "Schedule prompt human review and field verification",
    }
    return {
        "parcel_id": parcel["parcel_id"],
        "survey_number": parcel["survey_number"],
        "village": parcel["village"],
        "taluka": parcel["taluka"],
        "verification_status": parcel["verification_status"],
        "record_status": parcel["record_status"],
        "review_status": parcel["risk_status"],
        "change_percentage": change["change_percentage"] if change else None,
        "priority_score": score,
        "priority_level": level,
        "requires_field_verification": score >= 25,
        "factors": factors,
        "recommendation": recommendations[level],
        "score_version": SCORE_VERSION,
        "calculated_at": calculated_at or datetime.now(timezone.utc).isoformat(),
        "threshold_notice": "Priority thresholds are prototype workflow heuristics and are not government or legal standards.",
    }


def rank_priorities(*, level: str | None = None, min_score: int = 0, limit: int = 100, taluka: str | None = None, verification_status: str | None = None) -> list[dict]:
    results = [calculate_priority(feature["properties"]) for feature in PARCELS["features"]]
    if level:
        results = [item for item in results if item["priority_level"].lower() == level.lower()]
    if taluka:
        results = [item for item in results if item["taluka"].lower() == taluka.lower()]
    if verification_status:
        results = [item for item in results if item["verification_status"].lower() == verification_status.lower()]
    results = [item for item in results if item["priority_score"] >= min_score]
    results.sort(key=lambda item: (-item["priority_score"], item["parcel_id"]))
    for rank, item in enumerate(results[:limit], start=1):
        item["rank"] = rank
    return results[:limit]
