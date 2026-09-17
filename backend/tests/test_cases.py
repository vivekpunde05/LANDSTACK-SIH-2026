import json

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.services import cases, grievances


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
    app.dependency_overrides[get_db] = offline_db
    monkeypatch.setattr(grievances, "UPLOAD_ROOT", tmp_path.resolve())
    grievances.reset_fallback_store()
    cases.reset_fallback_store()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def submit_grievance(client, *, key="case-grievance-001", parcel="RTN-CHI-0013"):
    response = client.post(
        f"/api/parcels/{parcel}/grievances",
        data={"payload": json.dumps({
            "category": "Boundary / Parcel Concern",
            "description": "A parcel boundary concern is submitted for administrative review.",
        })},
        headers={"X-Idempotency-Key": key},
    )
    assert response.status_code == 200
    return response.json()


def open_case(client, grievance_id, key="open-case-key-001"):
    return client.post(
        f"/api/grievances/{grievance_id}/case",
        headers={"X-Idempotency-Key": key},
    )


def action(client, case_id, name, note="Administrative review action recorded for this demonstration case.", key=None, resolution_type=None):
    payload = {"action": name, "note": note}
    if resolution_type:
        payload["resolution_type"] = resolution_type
    return client.post(
        f"/api/cases/{case_id}/actions",
        json=payload,
        headers={"X-Idempotency-Key": key or f"{name}-key-001"},
    )


def test_create_case_detail_and_fallback(client):
    grievance = submit_grievance(client)
    response = open_case(client, grievance["grievance_id"])
    assert response.status_code == 200
    record = response.json()
    assert record["case_id"] == "CASE-2026-0001"
    assert record["case_status"] == "Open" and record["review_stage"] == "Intake"
    assert record["storage_mode"] == "fallback"
    detail = client.get(f"/api/cases/{record['case_id']}").json()
    assert detail["grievance"]["description"] == grievance["description"]
    assert detail["demo_session"]["actor_reference"] == "DEMO-ADMIN-01"


def test_duplicate_case_is_reused_without_duplicate_event(client):
    grievance = submit_grievance(client)
    first = open_case(client, grievance["grievance_id"], "open-case-first").json()
    second = open_case(client, grievance["grievance_id"], "open-case-second").json()
    assert second["case_id"] == first["case_id"]
    assert second["case_already_exists"] is True
    assert client.get(f"/api/cases/{first['case_id']}/events").json()["count"] == 1


def test_unknown_grievance_and_case(client):
    assert open_case(client, "GRV-2026-9999").status_code == 404
    assert client.get("/api/cases/CASE-2026-9999").status_code == 404
    assert client.get("/api/cases/CASE-2026-9999/events").status_code == 404


def test_case_queue_and_filters(client):
    first = submit_grievance(client, key="queue-grievance-one", parcel="RTN-CHI-0013")
    second = submit_grievance(client, key="queue-grievance-two", parcel="RTN-RAT-0002")
    open_case(client, first["grievance_id"], "queue-open-one")
    second_case = open_case(client, second["grievance_id"], "queue-open-two").json()
    action(client, second_case["case_id"], "start_review", key="queue-start-two")
    queue = client.get("/api/cases").json()
    assert queue["count"] == 2 and queue["items"][0]["case_id"] == second_case["case_id"]
    assert client.get("/api/cases", params={"status": "Under Review"}).json()["count"] == 1
    assert client.get("/api/cases", params={"stage": "Intake"}).json()["count"] == 1
    assert client.get("/api/cases", params={"taluka": "Ratnagiri"}).json()["count"] == 1
    assert client.get("/api/cases", params={"priority_level": "High Priority Review"}).json()["count"] >= 1


def test_start_review_and_invalid_direct_close(client):
    case = open_case(client, submit_grievance(client)["grievance_id"]).json()
    invalid = action(client, case["case_id"], "close_case", key="invalid-close")
    assert invalid.status_code == 400 and invalid.json()["detail"]["code"] == "invalid_transition"
    reviewed = action(client, case["case_id"], "start_review").json()
    assert reviewed["case_status"] == "Under Review"
    assert reviewed["review_stage"] == "Initial Review"


def test_field_verification_request_and_grievance_sync(client):
    grievance = submit_grievance(client)
    case = open_case(client, grievance["grievance_id"]).json()
    action(client, case["case_id"], "start_review")
    requested = action(client, case["case_id"], "request_field_verification").json()
    assert requested["case_status"] == "Field Verification Requested"
    assert requested["requires_field_verification"] is True
    tracking = client.get(f"/api/grievances/{grievance['grievance_id']}").json()
    assert tracking["status"] == "Field Verification Recommended"
    assert tracking["administrative_case"]["case_id"] == case["case_id"]


def test_more_information_round_trip(client):
    grievance = submit_grievance(client)
    case = open_case(client, grievance["grievance_id"]).json()
    action(client, case["case_id"], "start_review")
    requested = action(client, case["case_id"], "request_more_information").json()
    assert requested["requires_more_information"] is True
    assert client.get(f"/api/grievances/{grievance['grievance_id']}").json()["status"] == "More Information Required"
    resumed = action(client, case["case_id"], "start_review", key="resume-review-key")
    assert resumed.json()["case_status"] == "Under Review"


def test_ready_resolve_and_close_lifecycle(client):
    grievance = submit_grievance(client)
    case = open_case(client, grievance["grievance_id"]).json()
    action(client, case["case_id"], "start_review")
    ready = action(client, case["case_id"], "mark_ready_for_decision").json()
    assert ready["case_status"] == "Ready for Decision"
    missing_resolution = action(client, case["case_id"], "resolve_case", key="missing-resolution")
    assert missing_resolution.status_code == 422
    resolved = action(
        client, case["case_id"], "resolve_case",
        note="Available demonstration information has been reviewed and recorded.",
        key="resolve-with-data",
        resolution_type="No Further Action Required",
    ).json()
    assert resolved["case_status"] == "Resolved" and resolved["resolved_at"]
    closed = action(client, case["case_id"], "close_case", key="close-after-resolution").json()
    assert closed["case_status"] == "Closed" and closed["closed_at"]
    tracking = client.get(f"/api/grievances/{grievance['grievance_id']}").json()
    assert tracking["status"] == "Closed"
    assert tracking["administrative_case"]["resolution_type"] == "No Further Action Required"


def test_closed_case_blocks_actions_and_notes(client):
    case = open_case(client, submit_grievance(client)["grievance_id"]).json()
    action(client, case["case_id"], "start_review")
    action(client, case["case_id"], "mark_ready_for_decision")
    action(client, case["case_id"], "resolve_case", key="resolve-closed-case", resolution_type="Record Review Recommended")
    action(client, case["case_id"], "close_case", key="close-closed-case")
    assert action(client, case["case_id"], "start_review", key="closed-action").status_code == 400
    note = client.post(
        f"/api/cases/{case['case_id']}/notes",
        json={"review_note": "This note must not be accepted on a closed case."},
        headers={"X-Idempotency-Key": "closed-note-key"},
    )
    assert note.status_code == 400


def test_review_notes_are_events_and_not_in_citizen_tracking(client):
    grievance = submit_grievance(client)
    case = open_case(client, grievance["grievance_id"]).json()
    private_note = "Internal demonstration review note for the administrative timeline only."
    response = client.post(
        f"/api/cases/{case['case_id']}/notes",
        json={"review_note": private_note},
        headers={"X-Idempotency-Key": "private-review-note"},
    )
    assert response.status_code == 200
    events = client.get(f"/api/cases/{case['case_id']}/events").json()["items"]
    assert events[-1]["event_type"] == "Review Note Added" and events[-1]["note"] == private_note
    citizen = json.dumps(client.get(f"/api/grievances/{grievance['grievance_id']}").json())
    assert private_note not in citizen and "events" not in citizen


def test_action_idempotency_prevents_duplicate_events(client):
    case = open_case(client, submit_grievance(client)["grievance_id"]).json()
    first = action(client, case["case_id"], "start_review", key="same-admin-action")
    second = action(client, case["case_id"], "start_review", key="same-admin-action")
    assert first.status_code == second.status_code == 200
    assert second.json()["duplicate_action"] is True
    assert client.get(f"/api/cases/{case['case_id']}/events").json()["count"] == 2


def test_validation_and_safe_wording(client):
    case = open_case(client, submit_grievance(client)["grievance_id"]).json()
    assert action(client, case["case_id"], "unknown_action", key="invalid-action-key").status_code == 422
    short_note = client.post(
        f"/api/cases/{case['case_id']}/notes",
        json={"review_note": "short"},
        headers={"X-Idempotency-Key": "short-note-key"},
    )
    assert short_note.status_code == 422
    text = json.dumps(client.get(f"/api/cases/{case['case_id']}").json()).lower()
    assert not any(term in text for term in ("fraud confirmed", "encroachment confirmed", "violation confirmed", "illegal ownership"))
