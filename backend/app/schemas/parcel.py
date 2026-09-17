from datetime import datetime

from pydantic import BaseModel


class ParcelDetail(BaseModel):
    parcel_id: str
    survey_number: str
    village: str
    taluka: str
    district: str
    area_hectares: float
    land_type: str
    land_use: str
    record_status: str
    verification_status: str
    risk_status: str
    record_reference: str
    record_type: str
    source_label: str
    is_synthetic: bool
    created_at: datetime
    updated_at: datetime
    geometry: dict
