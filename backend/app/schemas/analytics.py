from typing import Any

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_parcels: int
    review_recommended_parcels: int
    satellite_analyses: int
    completed_inspections: int
    open_grievances: int
    active_cases: int
    resolved_or_closed_cases: int
    total_grievances: int
    total_inspections: int
    total_cases: int
    resolution_rate: float | None
    requires_follow_up_inspections: int
    storage_mode: str
    refreshed_at: str
    data_notice: str


class AnalyticsCollection(BaseModel):
    storage_mode: str
    refreshed_at: str
    model_config = {"extra": "allow"}


class AttentionCollection(BaseModel):
    count: int
    items: list[dict[str, Any]]
    storage_mode: str
    refreshed_at: str
