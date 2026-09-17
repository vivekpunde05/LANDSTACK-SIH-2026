from datetime import datetime

from fastapi.testclient import TestClient

from app.data import PARCELS
from app.main import app
from app.services.priority_engine import PRIORITY_WEIGHTS, calculate_priority, rank_priorities

client = TestClient(app)
PARCELS_BY_ID = {feature["properties"]["parcel_id"]: feature["properties"] for feature in PARCELS["features"]}
FIXED_TIME = "2026-09-14T00:00:00+00:00"


def test_all_scores_are_bounded_explainable_and_totaled() -> None:
    for parcel in PARCELS_BY_ID.values():
        result = calculate_priority(parcel, FIXED_TIME)
        assert 0 <= result["priority_score"] <= 100
        assert result["priority_score"] == sum(factor["points"] for factor in result["factors"])
        assert sum(factor["max_points"] for factor in result["factors"]) == 100
        assert all(factor["reason"] for factor in result["factors"])
        assert result["score_version"] == "phase4-v1"
        datetime.fromisoformat(result["calculated_at"])


def test_result_is_deterministic() -> None:
    parcel = PARCELS_BY_ID["RTN-CHI-0013"]
    assert calculate_priority(parcel, FIXED_TIME) == calculate_priority(parcel, FIXED_TIME)


def test_no_analysis_adds_no_satellite_or_recency_points() -> None:
    result = calculate_priority(PARCELS_BY_ID["RTN-RAT-0003"], FIXED_TIME)
    assert result["change_percentage"] is None
    assert result["factors"][0]["points"] == 0
    assert result["factors"][-1]["points"] == 0
    assert "no points added" in result["factors"][0]["reason"].lower()


def test_verified_normal_stable_parcel_is_low_priority() -> None:
    result = calculate_priority(PARCELS_BY_ID["RTN-RAT-0001"], FIXED_TIME)
    assert result["priority_score"] == 3
    assert result["priority_level"] == "Routine"


def test_significant_change_ranks_above_stable_parcel() -> None:
    significant = calculate_priority(PARCELS_BY_ID["RTN-CHI-0013"], FIXED_TIME)
    stable = calculate_priority(PARCELS_BY_ID["RTN-RAT-0001"], FIXED_TIME)
    assert significant["priority_score"] > stable["priority_score"]
    assert significant["priority_level"] == "High Priority Review"


def test_weights_are_centralized_and_total_100() -> None:
    assert PRIORITY_WEIGHTS == {"satellite_change": 40, "verification_status": 20, "record_status": 15, "review_status": 15, "recency": 10}
    assert sum(PRIORITY_WEIGHTS.values()) == 100


def test_no_prohibited_legal_conclusions() -> None:
    rendered = str(rank_priorities()).lower()
    prohibited = ("illegal", "fraud", "encroachment confirmed", "violation confirmed", "unauthorized ownership")
    assert not any(term in rendered for term in prohibited)


def test_priority_endpoint_and_unknown_parcel() -> None:
    response = client.get("/api/parcels/RTN-CHI-0013/priority")
    assert response.status_code == 200
    assert response.json()["priority_score"] == 68
    assert response.json()["persistence"] in ("stored", "not persisted — database unavailable")
    assert client.get("/api/parcels/UNKNOWN/priority").status_code == 404


def test_ranking_and_filters() -> None:
    ranked = client.get("/api/priorities").json()["items"]
    assert len(ranked) == 24
    assert [item["priority_score"] for item in ranked] == sorted((item["priority_score"] for item in ranked), reverse=True)
    assert ranked[0]["parcel_id"] == "RTN-CHI-0013"
    minimum = client.get("/api/priorities", params={"min_score": 50}).json()["items"]
    assert minimum and all(item["priority_score"] >= 50 for item in minimum)
    high = client.get("/api/priorities", params={"level": "High Priority Review"}).json()["items"]
    assert high and all(item["priority_level"] == "High Priority Review" for item in high)
    chiplun = client.get("/api/priorities", params={"taluka": "Chiplun", "verification_status": "Requires Verification"}).json()["items"]
    assert chiplun and all(item["taluka"] == "Chiplun" and item["verification_status"] == "Requires Verification" for item in chiplun)
