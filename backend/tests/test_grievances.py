import json

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.services import grievances


class OfflineSession:
    def execute(self, *_args, **_kwargs):
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("database unavailable")

    def rollback(self):
        return None


def offline_db():
    yield OfflineSession()


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    app.dependency_overrides[get_db] = offline_db
    monkeypatch.setattr(grievances, "UPLOAD_ROOT", tmp_path.resolve())
    grievances.reset_fallback_store()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def valid_payload(**overrides):
    payload = {
        "category": "Suspected Land-Use Change",
        "description": "A visible land-use difference is being reported for official review.",
    }
    payload.update(overrides)
    return payload


def submit(client, payload=None, files=None, key="grievance-key-001", parcel="RTN-CHI-0013"):
    return client.post(
        f"/api/parcels/{parcel}/grievances",
        data={"payload": json.dumps(payload or valid_payload())},
        files=files or [],
        headers={"X-Idempotency-Key": key},
    )


def test_valid_submission_id_history_detail_and_fallback(client):
    response = submit(client)
    assert response.status_code == 200
    record = response.json()
    assert record["grievance_id"] == "GRV-2026-0001"
    assert record["status"] == "Submitted"
    assert record["storage_mode"] == "fallback"
    assert "lost when the backend restarts" in record["storage_notice"]
    history = client.get("/api/parcels/RTN-CHI-0013/grievances").json()
    assert history["count"] == 1
    assert client.get(f"/api/grievances/{record['grievance_id']}").json()["parcel_id"] == "RTN-CHI-0013"


def test_unknown_parcel_and_reference(client):
    assert submit(client, parcel="UNKNOWN").status_code == 404
    assert client.get("/api/parcels/UNKNOWN/grievances").status_code == 404
    missing = client.get("/api/grievances/GRV-2026-9999")
    assert missing.status_code == 404
    assert missing.json()["detail"]["message"] == "No grievance found for this reference."


@pytest.mark.parametrize("category", ["Ownership Fraud", "Illegal Encroachment", "", "Hidden Category"])
def test_invalid_category_rejected(client, category):
    assert submit(client, valid_payload(category=category), key=f"bad-category-{len(category)}-{category[:2]}").status_code == 422


def test_other_requires_custom_category(client):
    assert submit(client, valid_payload(category="Other"), key="other-without-note").status_code == 422
    response = submit(client, valid_payload(category="Other", custom_category="Map label clarification"), key="other-with-note")
    assert response.status_code == 200
    assert response.json()["custom_category"] == "Map label clarification"


def test_description_length_validation(client):
    assert submit(client, valid_payload(description="too short"), key="short-description").status_code == 422
    assert submit(client, valid_payload(description="x" * 3001), key="long-description").status_code == 422


def test_photo_evidence_safe_filename_and_restricted_route(client):
    png = b"\x89PNG\r\n\x1a\n" + b"demo-grievance-image"
    response = submit(client, files=[("photos", ("../../support.png", png, "image/png"))])
    assert response.status_code == 200
    evidence = response.json()["evidence"][0]
    assert evidence["file_name"] == "support.png"
    image = client.get(evidence["url"])
    assert image.status_code == 200 and image.headers["content-type"] == "image/png"
    assert client.get(f"/api/grievances/WRONG/evidence/{evidence['evidence_id']}").status_code == 404


def test_photo_type_content_size_and_count_validation(client):
    assert submit(client, files=[("photos", ("note.txt", b"text", "text/plain"))], key="bad-type-file").status_code == 422
    assert submit(client, files=[("photos", ("fake.png", b"not-png", "image/png"))], key="bad-content-file").status_code == 422
    oversized = b"\xff\xd8\xff" + b"0" * (5 * 1024 * 1024)
    assert submit(client, files=[("photos", ("large.jpg", oversized, "image/jpeg"))], key="oversized-file").status_code == 413
    png = b"\x89PNG\r\n\x1a\n" + b"x"
    files = [("photos", (f"photo-{index}.png", png, "image/png")) for index in range(4)]
    assert submit(client, files=files, key="too-many-files").status_code == 422


def test_duplicate_submission_is_idempotent(client):
    first = submit(client, key="same-grievance-key").json()
    second = submit(client, key="same-grievance-key").json()
    assert first["grievance_id"] == second["grievance_id"]
    assert second["duplicate_submission"] is True
    assert client.get("/api/parcels/RTN-CHI-0013/grievances").json()["count"] == 1


def test_queue_filters_and_newest_first(client):
    submit(client, key="queue-first", parcel="RTN-CHI-0013")
    submit(client, valid_payload(category="Boundary / Parcel Concern"), key="queue-second", parcel="RTN-RAT-0002")
    queue = client.get("/api/grievances").json()
    assert queue["count"] == 2
    assert queue["items"][0]["grievance_id"] == "GRV-2026-0002"
    assert client.get("/api/grievances", params={"status": "Submitted"}).json()["count"] == 2
    category = client.get("/api/grievances", params={"category": "Boundary / Parcel Concern"}).json()
    assert category["count"] == 1 and category["items"][0]["parcel_id"] == "RTN-RAT-0002"
    assert client.get("/api/grievances", params={"taluka": "Chiplun"}).json()["count"] == 1
    assert client.get("/api/grievances", params={"parcel_id": "RTN-RAT-0002", "limit": 1}).json()["count"] == 1


def test_no_sensitive_fields_required_or_exposed(client):
    record = submit(client, valid_payload(
        citizen_display_name="Demo Citizen",
        contact_reference="DEMO-CONTACT-01",
    )).json()
    grievance_id = record["grievance_id"]
    responses = [
        record,
        client.get(f"/api/grievances/{grievance_id}").json(),
        client.get("/api/parcels/RTN-CHI-0013/grievances").json()["items"][0],
        client.get("/api/grievances").json()["items"][0],
    ]
    private_fields = (
        "aadhaar", "pan", "phone", "address", "religion", "caste",
        "political_information", "citizen_display_name", "contact_reference",
    )
    for response in responses:
        for field in private_fields:
            assert field not in response


def test_no_automatic_legal_conclusion(client):
    text = json.dumps(submit(client).json()).lower()
    assert not any(term in text for term in ("illegal", "fraud", "encroachment confirmed", "violation confirmed", "criminal"))
