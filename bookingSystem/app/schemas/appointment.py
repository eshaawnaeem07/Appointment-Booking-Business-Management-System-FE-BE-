from pydantic import BaseModel, field_validator
from datetime import datetime
from app.utils.enums import AppointmentStatus
from uuid import UUID
from datetime import date

class AppointmentCreate(BaseModel):
    service_id: UUID
    start_time: datetime
    walk_in_customer_id: UUID | None = None

    @field_validator('start_time', mode='before')
    @classmethod
    def validate_start_time(cls, v):
        if isinstance(v, str):
            # Handle ISO format datetime strings
            try:
                # Try ISO format with full precision
                if 'T' in v:
                    parts = v.split('T')
                    if len(parts) == 2:
                        time_part = parts[1]
                        # Ensure hour is zero-padded (HH:MM:SS format)
                        time_components = time_part.split(':')
                        if len(time_components) >= 1 and len(time_components[0]) == 1:
                            raise ValueError(f"Hour must be zero-padded (e.g., '05:00:00' not '5:00:00')")
                return datetime.fromisoformat(v)
            except ValueError as e:
                raise ValueError(f"start_time must be ISO format (YYYY-MM-DDTHH:MM:SS). Error: {str(e)}")
        return v

class AppointmentUpdate(BaseModel):
    start_time: datetime

class AppointmentUserOut(BaseModel):
    id: UUID
    email: str

    class Config:
        from_attributes = True

class AppointmentBusinessOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class AppointmentServiceOut(BaseModel):
    id: UUID
    name: str
    requires_deposit: bool = False

    class Config:
        from_attributes = True

class AppointmentCustomerOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
    
class AppointmentOut(BaseModel):
    id: UUID
    user_id: UUID | None = None
    business_id: UUID
    service_id: UUID

    start_time: datetime
    end_time: datetime

    status: AppointmentStatus
    walk_in_customer_id: UUID | None = None
    user: AppointmentUserOut | None = None
    business: AppointmentBusinessOut | None = None
    service: AppointmentServiceOut | None = None
    walk_in_customer: AppointmentCustomerOut | None = None

    class Config:
        from_attributes = True


class AppointmentStatusResponse(BaseModel):
    appointment_id: UUID
    status: AppointmentStatus

    class Config:
        from_attributes = True


class AvailableSlotsResponse(BaseModel):
    date: date
    available_slots: list[datetime]


class AvailableDaySlots(BaseModel):
    date: date
    available_slots: list[datetime]


class AvailableSlotsRangeResponse(BaseModel):
    days: list[AvailableDaySlots]
