from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .parcel import Base


class ParcelPriorityScore(Base):
    __tablename__ = "parcel_priority_scores"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parcel_id: Mapped[str] = mapped_column(ForeignKey("land_parcels.parcel_id", ondelete="CASCADE"), nullable=False)
    priority_score: Mapped[int] = mapped_column(Integer, nullable=False)
    priority_level: Mapped[str] = mapped_column(String(80), nullable=False)
    requires_field_verification: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score_version: Mapped[str] = mapped_column(String(32), nullable=False, default="phase4-v1")
    factor_breakdown: Mapped[list] = mapped_column(JSONB, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("parcel_id", "score_version", name="parcel_priority_scores_parcel_version_key"),
        Index("parcel_priority_scores_score_idx", "priority_score"),
        Index("parcel_priority_scores_level_idx", "priority_level"),
    )
