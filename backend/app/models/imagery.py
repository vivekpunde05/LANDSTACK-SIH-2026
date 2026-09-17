from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .parcel import Base


class ParcelImagery(Base):
    __tablename__ = "parcel_imagery"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parcel_id: Mapped[str] = mapped_column(ForeignKey("land_parcels.parcel_id", ondelete="CASCADE"), nullable=False)
    capture_date: Mapped[date] = mapped_column(Date, nullable=False)
    image_type: Mapped[str] = mapped_column(String(80), nullable=False)
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_label: Mapped[str] = mapped_column(String(120), nullable=False)
    resolution_m: Mapped[float | None] = mapped_column(Numeric(8, 2))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("parcel_imagery_parcel_id_idx", "parcel_id"),)


class ChangeAnalysis(Base):
    __tablename__ = "change_analysis"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parcel_id: Mapped[str] = mapped_column(ForeignKey("land_parcels.parcel_id", ondelete="CASCADE"), nullable=False)
    before_image_id: Mapped[int] = mapped_column(ForeignKey("parcel_imagery.id"), nullable=False)
    after_image_id: Mapped[int] = mapped_column(ForeignKey("parcel_imagery.id"), nullable=False)
    analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    changed_area_sqm: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    change_percentage: Mapped[float] = mapped_column(Numeric(8, 3), nullable=False)
    change_strength: Mapped[str] = mapped_column(String(32), nullable=False)
    change_status: Mapped[str] = mapped_column(String(80), nullable=False)
    analysis_method: Mapped[str] = mapped_column(String(160), nullable=False)
    requires_verification: Mapped[bool] = mapped_column(Boolean, nullable=False)
    result_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("change_analysis_parcel_id_idx", "parcel_id"),)
