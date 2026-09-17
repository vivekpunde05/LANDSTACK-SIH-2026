from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class AdministrativeCase(Base):
    __tablename__ = "administrative_cases"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    grievance_id: Mapped[str] = mapped_column(String(40), ForeignKey("citizen_grievances.grievance_id"), unique=True, index=True)
    parcel_id: Mapped[str] = mapped_column(String(32), ForeignKey("land_parcels.parcel_id"), index=True)
    case_status: Mapped[str] = mapped_column(String(50), index=True)
    review_stage: Mapped[str] = mapped_column(String(40), index=True)
    assigned_officer_display: Mapped[str] = mapped_column(String(100))
    assigned_officer_reference: Mapped[str] = mapped_column(String(80))
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    requires_field_verification: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_more_information: Mapped[bool] = mapped_column(Boolean, default=False)
    administrative_summary: Mapped[str | None] = mapped_column(Text)
    resolution_type: Mapped[str | None] = mapped_column(String(100))
    resolution_note: Mapped[str | None] = mapped_column(Text)
    latest_priority_score: Mapped[int] = mapped_column(Integer)
    latest_priority_level: Mapped[str] = mapped_column(String(40))
    storage_mode: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AdministrativeCaseEvent(Base):
    __tablename__ = "administrative_case_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(50), unique=True)
    action_key: Mapped[str | None] = mapped_column(String(80), unique=True)
    case_id: Mapped[str] = mapped_column(String(40), ForeignKey("administrative_cases.case_id"), index=True)
    event_type: Mapped[str] = mapped_column(String(60))
    from_status: Mapped[str | None] = mapped_column(String(50))
    to_status: Mapped[str | None] = mapped_column(String(50))
    from_stage: Mapped[str | None] = mapped_column(String(40))
    to_stage: Mapped[str | None] = mapped_column(String(40))
    note: Mapped[str] = mapped_column(Text)
    actor_display: Mapped[str] = mapped_column(String(100))
    actor_reference: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
