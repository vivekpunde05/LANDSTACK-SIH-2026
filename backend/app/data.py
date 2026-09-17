"""Deterministic, non-personal synthetic data for the LANDSTACK demonstration."""

from datetime import datetime, timezone
from typing import Any


def _ring(west: float, south: float, east: float, north: float) -> list[list[float]]:
    return [[west, south], [east, south], [east, north], [west, north], [west, south]]


def build_parcels() -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    base_lng, base_lat = 73.3032, 16.9908
    widths = [0.00235, 0.00265, 0.00215, 0.00255, 0.0024, 0.0027]
    heights = [0.00215, 0.00245, 0.00225, 0.00255]
    land_uses = ["Agricultural", "Orchard", "Residential", "Mixed"]
    land_types = ["Dry crop land", "Horticultural land", "Settlement land", "Mixed-use land"]
    verification = ["Verified", "Pending Verification", "Requires Verification"]
    risks = ["Normal", "Requires Verification", "Flagged for Review"]
    talukas = ["Ratnagiri", "Ratnagiri", "Chiplun", "Sangameshwar"]
    villages = ["Nachane Demo Village", "Mirjole Demo Village", "Chiplun Demo Village", "Sangameshwar Demo Village"]
    updated = datetime(2026, 8, 15, 10, 30, tzinfo=timezone.utc).isoformat()

    numeric_id = 1
    for row in range(4):
        x = base_lng
        for col in range(6):
            gap = 0.00018
            width, height = widths[col], heights[row]
            west = x + (0.00012 if row % 2 else 0)
            south = base_lat + sum(heights[:row]) + row * gap
            parcel_id = f"RTN-{talukas[row][:3].upper()}-{numeric_id:04d}"
            features.append({
                "type": "Feature",
                "id": parcel_id,
                "geometry": {"type": "Polygon", "coordinates": [_ring(west, south, west + width, south + height)]},
                "properties": {
                    "parcel_id": parcel_id,
                    "survey_number": f"SYN-{100 + numeric_id}",
                    "village": villages[row], "taluka": talukas[row], "district": "Ratnagiri",
                    "area_hectares": round(width * height * 12100 * 0.91, 2),
                    "land_type": land_types[(row + col) % 4], "land_use": land_uses[(row * 2 + col) % 4],
                    "record_status": "Under Review" if numeric_id % 7 == 0 else "Active",
                    "verification_status": verification[(row + col * 2) % 3],
                    "risk_status": risks[(row * 2 + col) % 3],
                    "record_reference": f"DEMO-REC-{numeric_id:04d}",
                    "record_type": "Synthetic Parcel Record", "source_label": "LANDSTACK Demo Dataset",
                    "is_synthetic": True, "created_at": updated, "updated_at": updated,
                },
            })
            x += width + gap
            numeric_id += 1
    return {"type": "FeatureCollection", "features": features}


PARCELS = build_parcels()
