import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base
from app.utils.enums import UserRole
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER.value)

    reset_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    refresh_token = Column(String, nullable=True)
    refresh_token_expiry = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ONE USER → ONE BUSINESS
    business = relationship("Business", back_populates="owner", uselist=False)

    # USER BOOKINGS
    appointments = relationship(
        "Appointment",
        foreign_keys="Appointment.user_id",
        back_populates="user"
    )