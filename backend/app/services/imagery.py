from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_ROOT = PROJECT_ROOT / "datasets" / "satellite"
GENERATED_ROOT = PROJECT_ROOT / "backend" / "generated"

DEMO_IMAGERY = {
    parcel_id: [
        {
            "id": index * 2 - 1,
            "parcel_id": parcel_id,
            "capture_date": "2023-01-01",
            "image_type": "Demo aerial-style imagery",
            "image_path": f"{parcel_id}/before.png",
            "image_url": f"/demo-assets/{parcel_id}/before.png",
            "source_label": "LANDSTACK Demo Imagery",
            "resolution_m": 1.0,
            "is_demo": True,
        },
        {
            "id": index * 2,
            "parcel_id": parcel_id,
            "capture_date": "2026-01-01",
            "image_type": "Demo aerial-style imagery",
            "image_path": f"{parcel_id}/after.png",
            "image_url": f"/demo-assets/{parcel_id}/after.png",
            "source_label": "LANDSTACK Demo Imagery",
            "resolution_m": 1.0,
            "is_demo": True,
        },
    ]
    for index, parcel_id in enumerate(("RTN-RAT-0001", "RTN-RAT-0002", "RTN-CHI-0013", "RTN-SAN-0019"), start=1)
}


def imagery_for(parcel_id: str) -> list[dict]:
    return DEMO_IMAGERY.get(parcel_id, [])


def resolve_image(parcel_id: str, capture_date: str) -> tuple[Path, dict] | None:
    for item in imagery_for(parcel_id):
        if item["capture_date"] == capture_date:
            return DATASET_ROOT / item["image_path"], item
    return None
