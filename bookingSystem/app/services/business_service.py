from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.business import Business
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate
from datetime import datetime
from app.utils.auth_utils import check_business_owner
from app.utils.db_utils import commit_and_refresh
from app.utils.helpers import get_business_or_404
from uuid import UUID

class BusinessService:
    def __init__(self, db: Session):
        self.db = db

    # GET ALL
    def get_all(self):
        try:
            return self.db.query(Business).filter(Business.is_deleted == False).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch businesses: {str(e)}")

    def get_mine(self, user: User):
        try:
            return self.db.query(Business).filter(
                Business.owner_id == user.id,
                Business.is_deleted == False
            ).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch businesses: {str(e)}")

    # GET BY ID
    def get_by_id(self, business_id: UUID):
        try:
            return get_business_or_404(self.db, business_id)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching business: {str(e)}")

    # CREATE BUSINESS (ONE USER → ONE BUSINESS)
    def create(self, user: User, data: BusinessCreate):
        try:
            existing = self.db.query(Business).filter(
                Business.owner_id == user.id,
                Business.is_deleted == False
            ).first()

            if existing:
                raise HTTPException(status_code=400, detail="User already owns a business")

            business = Business(
                owner_id=user.id,
                name=data.name,
                description=data.description
            )

            # update role → business
            user.role = "business"

            self.db.add(business)
            # USING UTILS HERE
            return commit_and_refresh(self.db, business)

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Business creation failed: {str(e)}")

    # UPDATE
    def update(self, user: User, business_id: UUID, data: BusinessUpdate):
        try:
            business = self.get_by_id(business_id)

            # USING AUTH UTILS
            check_business_owner(business, user.id)
            if data.name:
                business.name = data.name
            if data.description:
                business.description = data.description
            business.updated_at = datetime.utcnow()

            # USING DB UTILS
            return commit_and_refresh(self.db, business)
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Business update failed: {str(e)}")

    # SOFT DELETE
    def delete(self, user: User, business_id: UUID):
        try:
            business = self.get_by_id(business_id)
            # USING AUTH UTILS
            check_business_owner(business, user.id)

            business.is_deleted = True
            business.updated_at = datetime.utcnow()

            self.db.commit()
            return {"message": "Business deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Business deletion failed: {str(e)}")
