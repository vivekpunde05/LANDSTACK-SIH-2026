from pathlib import Path

import cv2
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.change_detection import ChangeDetectionError, analyze_change
from app.services.imagery import DATASET_ROOT, DEMO_IMAGERY

client = TestClient(app)


def test_imagery_list_and_unknown_parcel() -> None:
    response = client.get("/api/parcels/RTN-RAT-0001/imagery")
    assert response.status_code == 200
    assert [item["capture_date"] for item in response.json()] == ["2023-01-01", "2026-01-01"]
    assert all(item["is_demo"] for item in response.json())
    assert client.get("/api/parcels/UNKNOWN/imagery").status_code == 404


def test_valid_parcel_without_imagery_is_empty() -> None:
    response = client.get("/api/parcels/RTN-RAT-0003/imagery")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("parcel_id,expected_status", [
    ("RTN-RAT-0001", "No significant change detected"),
    ("RTN-RAT-0002", "Potential change"),
    ("RTN-CHI-0013", "Requires verification"),
    ("RTN-SAN-0019", "Requires verification"),
])
def test_change_results_are_deterministic_and_conservative(parcel_id: str, expected_status: str) -> None:
    payload = {"before_date": "2023-01-01", "after_date": "2026-01-01"}
    first = client.post(f"/api/parcels/{parcel_id}/change-analysis", json=payload)
    second = client.post(f"/api/parcels/{parcel_id}/change-analysis", json=payload)
    assert first.status_code == 200
    result, repeated = first.json(), second.json()
    assert result["change_status"] == expected_status
    assert result["change_percentage"] == repeated["change_percentage"]
    assert result["changed_area_sqm"] == repeated["changed_area_sqm"]
    assert "confidence" not in result
    assert result["overlay_url"].endswith("change-overlay.png")
    rendered = str(result).lower()
    assert not any(claim in rendered for claim in ("illegal ownership", "illegal construction", "encroachment confirmed", "violation confirmed"))


def test_date_validation_and_missing_imagery() -> None:
    reversed_dates = client.post("/api/parcels/RTN-RAT-0001/change-analysis", json={"before_date": "2026-01-01", "after_date": "2023-01-01"})
    assert reversed_dates.status_code == 422
    unavailable = client.post("/api/parcels/RTN-RAT-0001/change-analysis", json={"before_date": "2022-01-01", "after_date": "2026-01-01"})
    assert unavailable.status_code == 400


def test_engine_generates_mask_and_overlay(tmp_path: Path) -> None:
    items = DEMO_IMAGERY["RTN-RAT-0002"]
    result = analyze_change(DATASET_ROOT / items[0]["image_path"], DATASET_ROOT / items[1]["image_path"], tmp_path, 0.06)
    assert result["change_percentage"] > 2
    assert result["mask_path"].exists() and result["overlay_path"].exists()
    assert cv2.countNonZero(cv2.imread(str(result["mask_path"]), cv2.IMREAD_GRAYSCALE)) > 0


def test_engine_handles_missing_or_malformed_images(tmp_path: Path) -> None:
    missing = tmp_path / "missing.png"
    with pytest.raises(ChangeDetectionError, match="missing or malformed"):
        analyze_change(missing, missing, tmp_path / "out", 0.06)
