from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Boolean, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LandParcel(Base):
    __tablename__ = "land_parcels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parcel_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    survey_number: Mapped[str] = mapped_column(String(64), nullable=False)
    village: Mapped[str] = mapped_column(String(120), nullable=False)
    taluka: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[str] = mapped_column(String(120), nullable=False)
    area_hectares: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    land_type: Mapped[str] = mapped_column(String(80), nullable=False)
    land_use: Mapped[str] = mapped_column(String(80), nullable=False)
    record_status: Mapped[str] = mapped_column(String(80), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(80), nullable=False)
    risk_status: Mapped[str] = mapped_column(String(80), nullable=False)
    record_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    record_type: Mapped[str] = mapped_column(String(120), nullable=False)
    source_label: Mapped[str] = mapped_column(String(120), nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    geometry: Mapped[object] = mapped_column(Geometry("POLYGON", srid=4326, spatial_index=False), nullable=False)

    __table_args__ = (
        Index("land_parcels_geometry_gix", "geometry", postgresql_using="gist"),
        Index("land_parcels_parcel_id_idx", "parcel_id"),
        Index("land_parcels_survey_number_idx", "survey_number"),
        Index("land_parcels_village_idx", "village"),
        Index("land_parcels_taluka_idx", "taluka"),
        Index("land_parcels_land_use_idx", "land_use"),
        Index("land_parcels_verification_status_idx", "verification_status"),
        Index("land_parcels_risk_status_idx", "risk_status"),
    )
