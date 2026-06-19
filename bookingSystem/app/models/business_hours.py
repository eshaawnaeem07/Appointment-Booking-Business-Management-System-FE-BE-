from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
import uuid


class BusinessHours(Base):
    __tablename__ = "business_hours"

    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    is_open = Column(Boolean, default=False)

    business = relationship("Business", back_populates="hours")