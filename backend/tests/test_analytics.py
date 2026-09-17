import csv
import io
import json
import math

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.services import cases, grievances, inspections
from app.services.analytics import analytics_distributions
from app.services.priority_engine import rank_priorities


class OfflineSession:
    def execute(self, *_args, **_kwargs):
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("database unavailable")

    def rollback(self):
        return None


def offline_db():
    yield OfflineSession()


@pytest.fixture(autouse=True)
def isolated_stores(tmp_path, monkeypatch):
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = offline_db
    monkeypatch.setattr(grievances, "UPLOAD_ROOT", (tmp_path / "grievances").resolve())
    monkeypatch.setattr(inspections, "UPLOAD_ROOT", (tmp_path / "inspections").resolve())
    grievances.reset_fallback_store(); inspections.reset_fallback_store(); cases.reset_fallback_store()
    yield
    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


@pytest.fixture
def client():
    return TestClient(app)


def submit_grievance(client, *, category="Boundary / Parcel Concern", custom_category=None):
    payload = {"category": category, "description": "A synthetic parcel concern is submitted for administrative review."}
    if custom_category is not None:
        payload["custom_category"] = custom_category
    return client.post(
        "/api/parcels/RTN-CHI-0013/grievances",
        data={"payload": json.dumps(payload)}, headers={"X-Idempotency-Key": f"analytics-grievance-{category[:4]}"},
    ).json()


def submit_inspection(client):
    payload = {
        "inspection_outcome": "Requires Further Review", "latitude": 17.12,
        "longitude": 73.54, "gps_accuracy_m": 20, "location_source": "Manual",
        "observations": "Synthetic field observations recorded for analytics testing.",
        "requires_follow_up": True, "recommendation": "Request administrative review",
    }
    return client.post(
        "/api/parcels/RTN-CHI-0013/inspections",
        data={"payload": json.dumps(payload)}, headers={"X-Idempotency-Key": "analytics-inspection-001"},
    ).json()


def test_summary_is_derived_and_empty_workflows_are_safe(client):
    summary = client.get("/api/analytics/summary").json()
    assert summary["total_parcels"] == len(rank_priorities(limit=100))
    assert summary["review_recommended_parcels"] == sum(item["priority_level"] != "Routine" for item in rank_priorities(limit=100))
    assert summary["satellite_analyses"] == 4
    assert summary["completed_inspections"] == summary["open_grievances"] == summary["active_cases"] == 0
    assert summary["resolution_rate"] is None and summary["storage_mode"] == "fallback"


def test_distributions_total_and_percentage_are_finite(client):
    result = client.get("/api/analytics/distributions").json()
    assert sum(item["count"] for item in result["priority_levels"]) == 24
    assert sum(item["count"] for item in result["verification_statuses"]) == 24
    for distribution in ("priority_levels", "verification_statuses", "grievance_categories", "grievance_statuses", "case_statuses", "inspection_outcomes", "satellite_statuses"):
        assert all(math.isfinite(item["percentage"]) for item in result[distribution])


def test_explicit_zero_snapshot_has_no_nan_or_infinity():
    result = analytics_distributions({
        "parcels": [], "priorities": [], "analyses": [], "inspections": [],
        "grievances": [], "cases": [], "storage_mode": "fallback", "refreshed_at": "now",
    })
    assert result["average_satellite_change_percentage"] is None
    assert all(item["percentage"] == 0 for name, values in result.items() if isinstance(values, list) for item in values)


def test_geography_aggregation_matches_parcels(client):
    result = client.get("/api/analytics/geography").json()
    assert sum(item["parcel_count"] for item in result["talukas"]) == 24
    assert {item["taluka"] for item in result["talukas"]} == {"Ratnagiri", "Chiplun", "Sangameshwar"}
    assert sum(item["grievance_count"] for item in result["talukas"]) == 0


def test_workflow_metrics_and_attention_use_current_stores(client):
    grievance = submit_grievance(client)
    inspection = submit_inspection(client)
    opened = client.post(
        f"/api/grievances/{grievance['grievance_id']}/case",
        headers={"X-Idempotency-Key": "analytics-open-case"},
    ).json()
    summary = client.get("/api/analytics/summary").json()
    assert summary["total_grievances"] == summary["open_grievances"] == 1
    assert summary["total_inspections"] == summary["completed_inspections"] == 1
    assert summary["requires_follow_up_inspections"] == 1 and summary["active_cases"] == 1
    attention = client.get("/api/analytics/attention").json()
    assert any(item["reference"] == opened["case_id"] for item in attention["items"])
    assert inspection["inspection_id"].startswith("INSP-")


@pytest.mark.parametrize("name", ["parcels", "priorities", "grievances", "inspections", "cases"])
def test_csv_reports_download_as_utf8(name, client):
    if name == "grievances": submit_grievance(client)
    if name == "inspections": submit_inspection(client)
    if name == "cases":
        grievance = submit_grievance(client)
        client.post(f"/api/grievances/{grievance['grievance_id']}/case", headers={"X-Idempotency-Key": "csv-open-case"})
    response = client.get(f"/api/reports/{name}.csv")
    assert response.status_code == 200 and response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=" in response.headers["content-disposition"]
    rows = list(csv.DictReader(io.StringIO(response.text.lstrip("\ufeff"))))
    assert rows or name in {"grievances", "inspections", "cases"}


def test_csv_formula_injection_and_privacy(client):
    submit_grievance(client, category="Other", custom_category="=SUM(1,1)")
    response = client.get("/api/reports/grievances.csv")
    assert "'=SUM(1,1)" in response.text
    forbidden = ("citizen_display_name", "contact_reference", "file_path", "latitude", "longitude", "administrative_summary", "actor_reference")
    assert not any(value in response.text for value in forbidden)


def test_case_report_excludes_internal_notes_and_actor(client):
    grievance = submit_grievance(client)
    case = client.post(f"/api/grievances/{grievance['grievance_id']}/case", headers={"X-Idempotency-Key": "private-case-open"}).json()
    private_note = "Private administrative note that must not enter the report."
    client.post(f"/api/cases/{case['case_id']}/notes", json={"review_note": private_note}, headers={"X-Idempotency-Key": "private-case-note"})
    text = client.get("/api/reports/cases.csv").text
    assert private_note not in text and "DEMO-ADMIN-01" not in text
