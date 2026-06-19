from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.utils.enums import UserRole
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = UserRole.USER.value
    # @field_validator("role")
    # @classmethod
    # def validate_role(cls, v):
    #     if v not in [UserRole.USER.value, UserRole.BUSINESS.value]:
    #         raise ValueError ("Input should be 'user' or 'business'")
    #     return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str = UserRole.USER.value
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class otpRequest(BaseModel):
    email: EmailStr
    otp: str
