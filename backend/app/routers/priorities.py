from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..data import PARCELS
from ..database import get_db
from ..services.priority_engine import calculate_priority, rank_priorities
from ..services.priority_persistence import persist_priority

router = APIRouter(prefix="/api", tags=["inspection priority"])
DatabaseSession = Annotated[Session, Depends(get_db)]
PARCEL_INDEX = {feature["properties"]["parcel_id"]: feature["properties"] for feature in PARCELS["features"]}


@router.get("/parcels/{parcel_id}/priority")
def parcel_priority(parcel_id: str, db: DatabaseSession) -> dict:
    parcel = PARCEL_INDEX.get(parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail={"code": "parcel_not_found", "message": f"Parcel '{parcel_id}' was not found."})
    result = calculate_priority(parcel)
    result["persistence"] = "stored" if persist_priority(db, result) else "not persisted — database unavailable"
    return result


@router.get("/priorities")
def priority_queue(
    level: str | None = None,
    min_score: int = Query(default=0, ge=0, le=100),
    limit: int = Query(default=100, ge=1, le=100),
    taluka: str | None = None,
    verification_status: str | None = None,
) -> dict:
    items = rank_priorities(level=level, min_score=min_score, limit=limit, taluka=taluka, verification_status=verification_status)
    return {"type": "InspectionPriorityQueue", "count": len(items), "score_version": "phase4-v1", "items": items}
