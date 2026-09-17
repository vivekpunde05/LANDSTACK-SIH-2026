import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


SELECT_FIELDS = """
    parcel_id, survey_number, village, taluka, district,
    area_hectares::float AS area_hectares, land_type, land_use,
    record_status, verification_status, risk_status,
    record_reference, record_type, source_label, is_synthetic,
    created_at, updated_at, ST_AsGeoJSON(geometry)::json AS geometry
"""


def list_parcels(
    db: Session,
    *,
    village: str | None = None,
    taluka: str | None = None,
    land_use: str | None = None,
    verification_status: str | None = None,
    risk_status: str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    clauses = ["is_synthetic = TRUE"]
    params: dict[str, str] = {}
    filters = {
        "village": village,
        "taluka": taluka,
        "land_use": land_use,
        "verification_status": verification_status,
        "risk_status": risk_status,
    }
    for column, value in filters.items():
        if value:
            clauses.append(f"LOWER({column}) = LOWER(:{column})")
            params[column] = value
    if search and search.strip():
        clauses.append("(parcel_id ILIKE :search OR survey_number ILIKE :search OR village ILIKE :search)")
        params["search"] = f"%{search.strip()}%"

    query = text(f"SELECT {SELECT_FIELDS} FROM land_parcels WHERE {' AND '.join(clauses)} ORDER BY parcel_id")
    rows = db.execute(query, params).mappings().all()
    features = []
    for row in rows:
        data = dict(row)
        geometry = data.pop("geometry")
        if isinstance(geometry, str):
            geometry = json.loads(geometry)
        properties = {key: (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in data.items()}
        features.append({"type": "Feature", "id": properties["parcel_id"], "geometry": geometry, "properties": properties})
    return {"type": "FeatureCollection", "features": features}


def get_parcel(db: Session, parcel_id: str) -> dict[str, Any] | None:
    row = db.execute(
        text(f"SELECT {SELECT_FIELDS} FROM land_parcels WHERE parcel_id = :parcel_id AND is_synthetic = TRUE"),
        {"parcel_id": parcel_id},
    ).mappings().one_or_none()
    if row is None:
        return None
    data = dict(row)
    if isinstance(data["geometry"], str):
        data["geometry"] = json.loads(data["geometry"])
    return {key: (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in data.items()}


def database_status(db: Session) -> dict[str, str]:
    version = db.execute(text("SELECT PostGIS_Version()"))
    return {"database": "connected", "postgis": str(version.scalar_one())}
