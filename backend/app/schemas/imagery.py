from datetime import date

from pydantic import BaseModel, model_validator


class ChangeAnalysisRequest(BaseModel):
    before_date: date
    after_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.before_date >= self.after_date:
            raise ValueError("before_date must be earlier than after_date")
        return self
