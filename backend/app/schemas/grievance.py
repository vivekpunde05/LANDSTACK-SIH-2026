from typing import Literal

from pydantic import BaseModel, Field, model_validator

GrievanceCategory = Literal[
    "Land Record Correction Request",
    "Boundary / Parcel Concern",
    "Suspected Land-Use Change",
    "Access / Right-of-Way Concern",
    "Public Land Concern",
    "Record Information Request",
    "Other",
]


class GrievanceSubmission(BaseModel):
    category: GrievanceCategory
    custom_category: str | None = Field(default=None, max_length=120)
    description: str = Field(min_length=20, max_length=3000)
    citizen_display_name: str | None = Field(default=None, max_length=100)
    contact_reference: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def normalize_and_validate(self):
        self.description = self.description.strip()
        if len(self.description) < 20:
            raise ValueError("Description must contain at least 20 non-space characters")
        self.custom_category = self.custom_category.strip() if self.custom_category else None
        if self.category == "Other" and not self.custom_category:
            raise ValueError("A custom category note is required when category is Other")
        if self.category != "Other":
            self.custom_category = None
        self.citizen_display_name = self.citizen_display_name.strip() if self.citizen_display_name else None
        self.contact_reference = self.contact_reference.strip() if self.contact_reference else None
        return self
