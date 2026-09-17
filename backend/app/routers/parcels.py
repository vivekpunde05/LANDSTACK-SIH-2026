from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.parcels import get_parcel, list_parcels

router = APIRouter(prefix="/api/parcels", tags=["parcel intelligence"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("")
def parcels(
    db: DatabaseSession,
    village: str | None = None,
    taluka: str | None = None,
    land_use: str | None = None,
    verification_status: str | None = None,
    risk_status: str | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=120),
) -> dict:
    return list_parcels(
        db,
        village=village,
        taluka=taluka,
        land_use=land_use,
        verification_status=verification_status,
        risk_status=risk_status,
        search=search,
    )


@router.get("/{parcel_id}")
def parcel_detail(parcel_id: str, db: DatabaseSession) -> dict:
    parcel = get_parcel(db, parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail={"code": "parcel_not_found", "message": f"Parcel '{parcel_id}' was not found."})
    return parcel
