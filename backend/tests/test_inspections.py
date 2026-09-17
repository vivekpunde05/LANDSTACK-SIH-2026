import json

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.services import inspections


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
    monkeypatch.setattr(inspections, "UPLOAD_ROOT", tmp_path.resolve())
    inspections.reset_fallback_store()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def valid_payload(**overrides):
    payload = {
        "inspection_outcome": "Requires Further Review",
        "latitude": 17.12,
        "longitude": 73.54,
        "gps_accuracy_m": 18,
        "location_source": "Manual",
        "observations": "Visual ground-cover change observed during the synthetic field review.",
        "requires_follow_up": True,
        "recommendation": "Request senior review",
    }
    payload.update(overrides)
    return payload


def submit(client, payload=None, files=None, key="submission-key-001", parcel="RTN-CHI-0013"):
    return client.post(
        f"/api/parcels/{parcel}/inspections",
        data={"payload": json.dumps(payload or valid_payload())},
        files=files or [],
        headers={"X-Idempotency-Key": key},
    )


def test_create_history_detail_and_fallback_notice(client):
    response = submit(client)
    assert response.status_code == 200
    record = response.json()
    assert record["inspection_status"] == "Inspection Completed"
    assert record["storage_mode"] == "fallback"
    assert "lost when the backend restarts" in record["storage_notice"]
    history = client.get("/api/parcels/RTN-CHI-0013/inspections").json()
    assert history["count"] == 1
    assert client.get(f"/api/inspections/{record['inspection_id']}").json()["inspection_outcome"] == "Requires Further Review"


def test_unknown_parcel_and_inspection_return_404(client):
    assert submit(client, parcel="UNKNOWN").status_code == 404
    assert client.get("/api/parcels/UNKNOWN/inspections").status_code == 404
    assert client.get("/api/inspections/INSP-MISSING").status_code == 404


@pytest.mark.parametrize("field,value", [("latitude", 91), ("latitude", -91), ("longitude", 181), ("longitude", -181)])
def test_invalid_coordinates_rejected(client, field, value):
    assert submit(client, valid_payload(**{field: value}), key=f"invalid-{field}-{value}").status_code == 422


def test_required_fields_and_outcome_validation(client):
    assert submit(client, valid_payload(observations=" short "), key="short-observations").status_code == 422
    missing = valid_payload(); missing.pop("inspection_outcome")
    assert submit(client, missing, key="missing-outcome").status_code == 422
    assert submit(client, valid_payload(inspection_outcome="Violation Confirmed"), key="invalid-outcome").status_code == 422


def test_location_optional_only_when_unable_to_verify(client):
    no_location = {"latitude": None, "longitude": None, "gps_accuracy_m": None, "location_source": "Unavailable"}
    assert submit(client, valid_payload(**no_location), key="location-required").status_code == 422
    response = submit(client, valid_payload(inspection_outcome="Unable To Verify", **no_location), key="location-optional")
    assert response.status_code == 200 and response.json()["location"] is None


def test_photo_validation_and_safe_filename(client):
    png = b"\x89PNG\r\n\x1a\n" + b"demo-pixels"
    response = submit(client, files=[("photos", ("../../field.png", png, "image/png"))])
    assert response.status_code == 200
    evidence = response.json()["evidence"][0]
    assert evidence["file_name"] == "field.png"
    image = client.get(evidence["url"])
    assert image.status_code == 200 and image.headers["content-type"] == "image/png"


def test_unsupported_mismatched_and_oversized_photos_rejected(client):
    assert submit(client, files=[("photos", ("note.txt", b"hello", "text/plain"))], key="bad-type-photo").status_code == 422
    assert submit(client, files=[("photos", ("fake.png", b"not a png", "image/png"))], key="bad-content-photo").status_code == 422
    oversized = b"\xff\xd8\xff" + b"0" * (5 * 1024 * 1024)
    assert submit(client, files=[("photos", ("large.jpg", oversized, "image/jpeg"))], key="large-photo").status_code == 413


def test_maximum_three_photos(client):
    png = b"\x89PNG\r\n\x1a\n" + b"x"
    files = [("photos", (f"photo-{index}.png", png, "image/png")) for index in range(4)]
    assert submit(client, files=files, key="too-many-photos").status_code == 422


def test_idempotency_prevents_duplicate_records(client):
    first = submit(client, key="same-submission-key").json()
    second = submit(client, key="same-submission-key").json()
    assert first["inspection_id"] == second["inspection_id"]
    assert second["duplicate_submission"] is True
    assert client.get("/api/parcels/RTN-CHI-0013/inspections").json()["count"] == 1


def test_existing_runtime_directory_is_not_overwritten(client, tmp_path):
    existing = tmp_path / "INSP-2026-0001"
    existing.mkdir()
    marker = existing / "existing-evidence.txt"
    marker.write_text("preserve")
    record = submit(client, key="restart-safe-inspection").json()
    assert record["inspection_id"] == "INSP-2026-0002"
    assert marker.read_text() == "preserve"


def test_missing_or_invalid_idempotency_key_rejected(client):
    missing = client.post("/api/parcels/RTN-CHI-0013/inspections", data={"payload": json.dumps(valid_payload())})
    assert missing.status_code == 422
    assert submit(client, key="bad key").status_code == 422


def test_response_contains_no_legal_conclusion(client):
    text = json.dumps(submit(client).json()).lower()
    assert not any(term in text for term in ("illegal", "fraud", "encroachment confirmed", "violation confirmed", "criminal"))
