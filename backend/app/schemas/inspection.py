from typing import Literal

from pydantic import BaseModel, Field, model_validator

InspectionOutcome = Literal[
    "No Significant Issue Observed",
    "Requires Further Review",
    "Change Confirmed On Site",
    "Unable To Verify",
]
LocationSource = Literal["Browser GPS", "Manual", "Unavailable"]


class InspectionSubmission(BaseModel):
    inspection_outcome: InspectionOutcome
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    gps_accuracy_m: float | None = Field(default=None, ge=0, le=100000)
    location_source: LocationSource = "Unavailable"
    officer_display_name: str = Field(default="Demo Field Officer", min_length=2, max_length=100)
    officer_reference: str = Field(default="DEMO-OFFICER-01", min_length=2, max_length=60)
    observations: str = Field(min_length=10, max_length=2000)
    recommendation: str | None = Field(default=None, max_length=1000)
    requires_follow_up: bool = False

    @model_validator(mode="after")
    def validate_location(self):
        has_latitude = self.latitude is not None
        has_longitude = self.longitude is not None
        if has_latitude != has_longitude:
            raise ValueError("Latitude and longitude must be provided together")
        if self.inspection_outcome != "Unable To Verify" and not (has_latitude and has_longitude):
            raise ValueError("A valid location is required unless the outcome is Unable To Verify")
        if self.location_source != "Unavailable" and not (has_latitude and has_longitude):
            raise ValueError("Selected location source requires valid coordinates")
        self.observations = self.observations.strip()
        if len(self.observations) < 10:
            raise ValueError("Inspection observations must contain at least 10 non-space characters")
        if self.recommendation is not None:
            self.recommendation = self.recommendation.strip() or None
        return self
