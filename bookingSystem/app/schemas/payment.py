from pydantic import BaseModel
from app.utils.enums import PaymentStatus
from datetime import datetime
from uuid import UUID


class PaymentCreateSession(BaseModel):
    appointment_id: UUID


class PaymentOut(BaseModel):
    id: UUID
    appointment_id: UUID
    status: PaymentStatus
    amount: int
    stripe_session_id: str | None = None
    stripe_payment_intent: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    appointment_id: UUID
    status: PaymentStatus
    amount: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str | None = None
    payment_id: UUID