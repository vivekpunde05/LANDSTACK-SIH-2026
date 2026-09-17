"""Idempotently seed the 24 LANDSTACK synthetic demonstration parcels."""
import json
import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.data import PARCELS  # noqa: E402
from app.services.imagery import DEMO_IMAGERY  # noqa: E402


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required. Export it from your local .env before seeding.")
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


UPSERT = """
INSERT INTO land_parcels (
 parcel_id, survey_number, village, taluka, district, area_hectares, land_type, land_use,
 record_status, verification_status, risk_status, record_reference, record_type, source_label,
 is_synthetic, created_at, updated_at, geometry
) VALUES (
 %(parcel_id)s, %(survey_number)s, %(village)s, %(taluka)s, %(district)s, %(area_hectares)s,
 %(land_type)s, %(land_use)s, %(record_status)s, %(verification_status)s, %(risk_status)s,
 %(record_reference)s, %(record_type)s, %(source_label)s, TRUE, %(created_at)s, %(updated_at)s,
 ST_SetSRID(ST_GeomFromGeoJSON(%(geometry)s), 4326)
) ON CONFLICT (parcel_id) DO UPDATE SET
 survey_number=EXCLUDED.survey_number, village=EXCLUDED.village, taluka=EXCLUDED.taluka,
 district=EXCLUDED.district, area_hectares=EXCLUDED.area_hectares, land_type=EXCLUDED.land_type,
 land_use=EXCLUDED.land_use, record_status=EXCLUDED.record_status,
 verification_status=EXCLUDED.verification_status, risk_status=EXCLUDED.risk_status,
 record_reference=EXCLUDED.record_reference, record_type=EXCLUDED.record_type,
 source_label=EXCLUDED.source_label, is_synthetic=TRUE, updated_at=EXCLUDED.updated_at,
 geometry=EXCLUDED.geometry;
"""

UPSERT_IMAGERY = """
INSERT INTO parcel_imagery (
 parcel_id, capture_date, image_type, image_path, source_label, resolution_m, is_demo
) VALUES (
 %(parcel_id)s, %(capture_date)s, %(image_type)s, %(image_path)s,
 %(source_label)s, %(resolution_m)s, TRUE
) ON CONFLICT (parcel_id, capture_date) DO UPDATE SET
 image_type=EXCLUDED.image_type, image_path=EXCLUDED.image_path,
 source_label=EXCLUDED.source_label, resolution_m=EXCLUDED.resolution_m, is_demo=TRUE;
"""


def main() -> None:
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            for feature in PARCELS["features"]:
                cursor.execute(UPSERT, {**feature["properties"], "geometry": json.dumps(feature["geometry"])})
            for items in DEMO_IMAGERY.values():
                for item in items:
                    cursor.execute(UPSERT_IMAGERY, item)
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT parcel_id), BOOL_AND(ST_IsValid(geometry)) FROM land_parcels WHERE is_synthetic=TRUE")
            count, distinct_count, all_valid = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM parcel_imagery WHERE is_demo=TRUE")
            imagery_count = cursor.fetchone()[0]
        connection.commit()
    print(f"Seed complete: {count} synthetic parcels; {distinct_count} unique IDs; geometry valid={all_valid}; {imagery_count} demo images")


if __name__ == "__main__":
    main()
