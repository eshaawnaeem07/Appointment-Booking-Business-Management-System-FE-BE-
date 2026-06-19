from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID

class CustomerBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=15)
    email: EmailStr

class CustomerCreate(CustomerBase):
    """Email is required when creating a customer"""
    pass

class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Ensure email is not empty string if provided"""
        if v is not None and isinstance(v, str) and v.strip() == "":
            raise ValueError("Email cannot be empty")
        return v

class CustomerOut(CustomerBase):
    id: UUID
    business_id: UUID
    user_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True
