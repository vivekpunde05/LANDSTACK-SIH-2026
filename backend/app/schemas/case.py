from typing import Literal

from pydantic import BaseModel, Field, model_validator

CaseActionName = Literal[
    "start_review",
    "request_field_verification",
    "request_more_information",
    "mark_ready_for_decision",
    "resolve_case",
    "close_case",
]

ResolutionType = Literal[
    "No Further Action Required",
    "Record Review Recommended",
    "Field Verification Completed",
    "Additional Documentation Required",
    "Referred for Further Administrative Review",
    "Information Updated in Case Record",
    "Unable to Conclude from Available Evidence",
]


class CaseAction(BaseModel):
    action: CaseActionName
    note: str = Field(min_length=10, max_length=3000)
    resolution_type: ResolutionType | None = None

    @model_validator(mode="after")
    def normalize_and_validate(self):
        self.note = self.note.strip()
        if len(self.note) < 10:
            raise ValueError("Administrative action note must contain at least 10 non-space characters")
        if self.action == "resolve_case" and self.resolution_type is None:
            raise ValueError("A resolution type is required to resolve a case")
        if self.action != "resolve_case":
            self.resolution_type = None
        return self


class CaseNote(BaseModel):
    review_note: str = Field(min_length=10, max_length=3000)

    @model_validator(mode="after")
    def normalize(self):
        self.review_note = self.review_note.strip()
        if len(self.review_note) < 10:
            raise ValueError("Review note must contain at least 10 non-space characters")
        return self
