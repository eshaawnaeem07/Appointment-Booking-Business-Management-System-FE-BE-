from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.db.enum_type import EnumValueType
from app.utils.enums import AppointmentStatus
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Appointment(Base):
    __tablename__ = "appointments"

    # id = Column(Integer, primary_key=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # business_id = Column(String, ForeignKey("businesses.id"))
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"))
    service_id = Column(UUID(as_uuid=True),ForeignKey("services.id"),nullable=False)
    
    # walk_in_customer_id = Column(Integer, ForeignKey("business_customers.id"), nullable=True)
    walk_in_customer_id = Column(UUID(as_uuid=True),ForeignKey("business_customers.id"),nullable=True)

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    status = Column(EnumValueType(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)


    user = relationship("User", back_populates="appointments")
    business = relationship("Business", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")

    payment = relationship("Payment", back_populates="appointment", uselist=False)
    walk_in_customer = relationship("BusinessCustomer", back_populates="appointments")
