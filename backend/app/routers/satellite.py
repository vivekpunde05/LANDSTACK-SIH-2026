from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..data import PARCELS
from ..schemas.imagery import ChangeAnalysisRequest
from ..services.change_detection import ChangeDetectionError, analyze_change
from ..services.imagery import GENERATED_ROOT, imagery_for, resolve_image

router = APIRouter(prefix="/api/parcels", tags=["satellite history"])
PARCEL_INDEX = {feature["properties"]["parcel_id"]: feature for feature in PARCELS["features"]}


def require_parcel(parcel_id: str) -> dict:
    parcel = PARCEL_INDEX.get(parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail={"code": "parcel_not_found", "message": f"Parcel '{parcel_id}' was not found."})
    return parcel


@router.get("/{parcel_id}/imagery")
def parcel_imagery(parcel_id: str) -> list[dict]:
    require_parcel(parcel_id)
    return imagery_for(parcel_id)


@router.post("/{parcel_id}/change-analysis")
def run_change_analysis(parcel_id: str, request: ChangeAnalysisRequest) -> dict:
    parcel = require_parcel(parcel_id)
    before = resolve_image(parcel_id, request.before_date.isoformat())
    after = resolve_image(parcel_id, request.after_date.isoformat())
    if before is None or after is None:
        raise HTTPException(status_code=400, detail={"code": "imagery_not_found", "message": "Imagery is unavailable for one or both selected dates."})
    try:
        result = analyze_change(
            before[0], after[0],
            GENERATED_ROOT / parcel_id / f"{request.before_date}_{request.after_date}",
            float(parcel["properties"]["area_hectares"]),
        )
    except ChangeDetectionError as exc:
        raise HTTPException(status_code=422, detail={"code": "analysis_failed", "message": str(exc)}) from exc

    relative = f"{parcel_id}/{request.before_date}_{request.after_date}"
    result.pop("mask_path")
    result.pop("overlay_path")
    return {
        "parcel_id": parcel_id,
        "before_date": request.before_date.isoformat(),
        "after_date": request.after_date.isoformat(),
        "analysis_date": datetime.now(timezone.utc).isoformat(),
        **result,
        "mask_url": f"/generated/{relative}/change-mask.png",
        "overlay_url": f"/generated/{relative}/change-overlay.png",
        "threshold_notice": "Prototype heuristic thresholds; not a legal or government standard.",
        "legal_notice": "Automated change detection is indicative only and does not constitute a legal determination.",
    }
