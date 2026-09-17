from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .parcel import Base


class CitizenGrievance(Base):
    __tablename__ = "citizen_grievances"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    grievance_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    submission_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    parcel_id: Mapped[str] = mapped_column(ForeignKey("land_parcels.parcel_id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    custom_category: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Submitted")
    priority_reference: Mapped[str | None] = mapped_column(String(40))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    requires_field_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolution_note: Mapped[str | None] = mapped_column(Text)
    storage_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    citizen_display_name: Mapped[str | None] = mapped_column(String(100))
    contact_reference: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("citizen_grievances_parcel_idx", "parcel_id"),
        Index("citizen_grievances_category_idx", "category"),
        Index("citizen_grievances_status_idx", "status"),
        Index("citizen_grievances_submitted_idx", "submitted_at"),
    )


class GrievanceEvidence(Base):
    __tablename__ = "grievance_evidence"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    grievance_id: Mapped[str] = mapped_column(ForeignKey("citizen_grievances.grievance_id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    caption: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("grievance_id", "evidence_id", name="grievance_evidence_public_key"),)
