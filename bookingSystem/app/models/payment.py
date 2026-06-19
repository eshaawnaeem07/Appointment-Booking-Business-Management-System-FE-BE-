from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.db.enum_type import EnumValueType
from app.utils.enums import PaymentStatus
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Payment(Base):
    __tablename__ = "payments"

    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)

    stripe_session_id = Column(String, nullable=True)
    stripe_payment_intent = Column(String, nullable=True)

    status = Column(EnumValueType(PaymentStatus), default=PaymentStatus.PENDING)
    amount = Column(Integer, nullable=False)  # amount in cents
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="payment")
