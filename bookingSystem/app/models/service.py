from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
import uuid

class Service(Base):
    __tablename__ = "services"

    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)

    # business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String)

    duration = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    requires_deposit = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    business = relationship("Business", back_populates="services")
    appointments = relationship("Appointment", back_populates="service")