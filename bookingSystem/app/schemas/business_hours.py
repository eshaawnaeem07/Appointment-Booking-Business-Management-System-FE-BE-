from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from uuid import UUID
from app.utils.enums import DayEnum
from datetime import time

# SINGLE HOUR SCHEMA
class BusinessHourBase(BaseModel):
    day_of_week: DayEnum
    is_open: bool
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    @field_validator("day_of_week", mode="before")
    @classmethod
    def normalize_day(cls, v):
        if isinstance(v, str):
            v = v.strip().lower()
            mapping = {
                "mon": "Monday",
                "monday": "Monday",
                "tue": "Tuesday",
                "tuesday": "Tuesday",
                "wed": "Wednesday",
                "wednesday": "Wednesday",
                "thu": "Thursday",
                "thursday": "Thursday",
                "fri": "Friday",
                "friday": "Friday",
                "sat": "Saturday",
                "saturday": "Saturday",
                "sun": "Sunday",
                "sunday": "Sunday",
            }
            if v in mapping:
                return mapping[v]
        return v

    @field_validator("open_time", "close_time")
    @classmethod
    def normalize_time(cls, v):
        if v is None:
            return v

        v = str(v)

        if v.isdigit():
            return f"{int(v):02d}:00:00"

        parts = v.split(":")
        if len(parts) == 2:
            return f"{v}:00"

        if len(parts) == 3:
            return v

        raise ValueError("Invalid time format")
    @model_validator(mode="after")
    def validate_business_hours(self):
        if self.is_open:
            if not self.open_time or not self.close_time:
                raise ValueError(
                    "Open and close times are required when business is open"
                )

        return self


# CREATE 
class BusinessHourCreate(BusinessHourBase):
    pass

# UPDATE
class BusinessHourUpdate(BaseModel):
    day_of_week: Optional[DayEnum] = None
    is_open: Optional[bool] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    @field_validator("day_of_week", mode="before")
    @classmethod
    def normalize_day(cls, v):
        if v is None:
            return v

        if isinstance(v, str):
            v = v.strip().lower()

            mapping = {
                "mon": "Monday",
                "monday": "Monday",
                "tue": "Tuesday",
                "tuesday": "Tuesday",
                "wed": "Wednesday",
                "wednesday": "Wednesday",
                "thu": "Thursday",
                "thursday": "Thursday",
                "fri": "Friday",
                "friday": "Friday",
                "sat": "Saturday",
                "saturday": "Saturday",
                "sun": "Sunday",
                "sunday": "Sunday",
            }

            if v in mapping:
                return mapping[v]

        return v

    @field_validator("open_time", "close_time", mode="before")
    @classmethod
    def normalize_time_values(cls, v):
        if v is None:
            return v

        v = str(v)

        if v.isdigit():
            return f"{int(v):02d}:00:00"

        parts = v.split(":")

        if len(parts) == 2:
            return f"{v}:00"

        return v

    @model_validator(mode="after")
    def validate_open_close_logic(self):

        if self.is_open is True:
            if not self.open_time or not self.close_time:
                raise ValueError(
                    "Open and close times are required when business is open"
                )

        return self
# RESPONSE
class BusinessHourOut(BaseModel):
    id: UUID
    business_id: UUID
    day_of_week: DayEnum # want to see "Monday" in JSON
    is_open: bool
    open_time: Optional[str] 
    close_time: Optional[str]

    class Config:
        from_attributes = True 