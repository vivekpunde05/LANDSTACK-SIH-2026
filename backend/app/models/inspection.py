from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .parcel import Base


class FieldInspection(Base):
    __tablename__ = "field_inspections"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    inspection_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    submission_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    parcel_id: Mapped[str] = mapped_column(ForeignKey("land_parcels.parcel_id", ondelete="CASCADE"), nullable=False)
    inspection_status: Mapped[str] = mapped_column(String(40), nullable=False)
    inspection_outcome: Mapped[str] = mapped_column(String(80), nullable=False)
    inspection_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    gps_accuracy_m: Mapped[float | None] = mapped_column(Float)
    location_source: Mapped[str] = mapped_column(String(40), nullable=False)
    officer_display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    officer_reference: Mapped[str] = mapped_column(String(60), nullable=False)
    observations: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text)
    priority_score_at_inspection: Mapped[int] = mapped_column(Integer, nullable=False)
    priority_level_at_inspection: Mapped[str] = mapped_column(String(80), nullable=False)
    satellite_change_percentage_at_inspection: Mapped[float | None] = mapped_column(Float)
    requires_follow_up: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index("field_inspections_parcel_idx", "parcel_id"),
        Index("field_inspections_status_idx", "inspection_status"),
        Index("field_inspections_outcome_idx", "inspection_outcome"),
        Index("field_inspections_date_idx", "inspection_date"),
    )


class InspectionEvidence(Base):
    __tablename__ = "inspection_evidence"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    inspection_id: Mapped[str] = mapped_column(ForeignKey("field_inspections.inspection_id", ondelete="CASCADE"), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(20), nullable=False, default="Photo")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    caption: Mapped[str | None] = mapped_column(String(500))
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("inspection_id", "evidence_id", name="inspection_evidence_public_key"),)
