from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class BusinessBase(BaseModel):
    name: str
    description: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


# class BusinessOut(BusinessBase):
#     id: str

#     class Config:
#         from_attributes = True

# class BusinessResponse(BaseModel):
#     id: UUID
#     name: str
#     description: str | None
#     owner_id: int
#     created_at: datetime
class BusinessOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True