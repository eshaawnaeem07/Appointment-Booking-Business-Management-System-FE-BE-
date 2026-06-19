from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
import uuid



class BusinessCustomer(Base):
    __tablename__ = "business_customers"

    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)

    # business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    name = Column(String, nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String, nullable=False)  # Email is required for sending payment/confirmation links
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="customers")
    appointments = relationship("Appointment", back_populates="walk_in_customer")