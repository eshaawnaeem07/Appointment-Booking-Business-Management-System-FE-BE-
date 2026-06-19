from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class Business(Base):
    __tablename__ = "businesses"
    # id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String)

    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    # hours = Column(JSON, default=list)

    owner = relationship("User", back_populates="business")

    services = relationship("Service", back_populates="business")  
    # hours = relationship("BusinessHours", back_populates="business") 
    hours = relationship("BusinessHours", back_populates="business", cascade="all, delete-orphan")

    appointments = relationship("Appointment", back_populates="business") 

    customers = relationship("BusinessCustomer", back_populates="business")