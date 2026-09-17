from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.data import PARCELS
from app.database import get_db
from app.main import app


class FakeMappings:
    def __init__(self, rows): self.rows = rows
    def all(self): return self.rows
    def one_or_none(self): return self.rows[0] if self.rows else None


class FakeResult:
    def __init__(self, rows=None, scalar=None): self.rows, self.scalar = rows or [], scalar
    def mappings(self): return FakeMappings(self.rows)
    def scalar_one(self): return self.scalar


class FakePostGISSession:
    def execute(self, statement, params=None):
        sql, params = str(statement), params or {}
        if "PostGIS_Version" in sql: return FakeResult(scalar="3.4 USE_GEOS=1")
        features = PARCELS["features"]
        if "WHERE parcel_id =" in sql:
            features = [f for f in features if f["properties"]["parcel_id"] == params["parcel_id"]]
        for key in ("village", "taluka", "land_use", "verification_status", "risk_status"):
            if params.get(key): features = [f for f in features if f["properties"][key].lower() == params[key].lower()]
        if params.get("search"):
            term = params["search"].strip("%").lower()
            features = [f for f in features if any(term in f["properties"][key].lower() for key in ("parcel_id", "survey_number", "village"))]
        rows = []
        for feature in features:
            props = dict(feature["properties"])
            props["created_at"] = datetime.fromisoformat(props["created_at"])
            props["updated_at"] = datetime.fromisoformat(props["updated_at"])
            props["geometry"] = feature["geometry"]
            rows.append(props)
        return FakeResult(rows=rows)


def override_db(): yield FakePostGISSession()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_health_reports_postgis() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"
    assert response.json()["project"] == "LANDSTACK"


def test_all_parcels_are_valid_synthetic_geojson() -> None:
    data = client.get("/api/parcels").json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 24
    assert len({f["properties"]["parcel_id"] for f in data["features"]}) == 24
    assert all(f["geometry"]["type"] == "Polygon" for f in data["features"])
    assert all(f["properties"]["is_synthetic"] for f in data["features"])


def test_parcel_detail_and_not_found() -> None:
    response = client.get("/api/parcels/RTN-RAT-0001")
    assert response.status_code == 200
    assert response.json()["record_reference"] == "DEMO-REC-0001"
    missing = client.get("/api/parcels/UNKNOWN")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "parcel_not_found"


def test_search_is_partial_and_case_insensitive() -> None:
    features = client.get("/api/parcels", params={"search": "syn-10"}).json()["features"]
    assert len(features) == 9


def test_all_filters() -> None:
    cases = {"taluka": "Chiplun", "land_use": "Agricultural", "verification_status": "Verified", "risk_status": "Flagged for Review"}
    for key, value in cases.items():
        features = client.get("/api/parcels", params={key: value}).json()["features"]
        assert features
        assert all(f["properties"][key] == value for f in features)


def test_schema_and_seed_safety_contract() -> None:
    root = Path(__file__).resolve().parents[2]
    schema = (root / "database/schema.sql").read_text()
    seed = (root / "database/seed_parcels.py").read_text()
    assert "geometry(Polygon, 4326)" in schema
    assert "USING GIST (geometry)" in schema
    assert "UNIQUE" in schema and "is_synthetic" in schema
    assert "ON CONFLICT (parcel_id) DO UPDATE" in seed
    assert not any(term in schema.lower() for term in ("aadhaar", "phone_number", "owner_name"))
