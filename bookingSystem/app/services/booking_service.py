from app.models.service import Service
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.utils.helpers import get_business_or_404
from app.utils.auth_utils import check_business_owner, check_service_owner
from app.utils.db_utils import commit_and_refresh


class ServiceService:

    @staticmethod
    def get_by_business(db: Session, business_id: UUID):
        try:
            return db.query(Service).filter(
                Service.business_id == business_id,
                Service.is_active == True
            ).all()
        except Exception:
            raise HTTPException(500, "Database error")

    @staticmethod
    def get_by_id(db: Session, service_id: UUID):
        try:
            return db.query(Service).filter(
                Service.id == service_id,
                Service.is_active == True
            ).first()
        except Exception:
            raise HTTPException(500, "Database error")

    @staticmethod
    def create_service(db: Session, business_id: UUID, user_id, payload):
        try:
            business = get_business_or_404(db, business_id)
            check_business_owner(business, user_id)

            existing = db.query(Service).filter(
                Service.business_id == business_id,
                Service.name == payload.name
            ).first()

            if existing:
                raise HTTPException(400, "Service already exists")

            service = Service(
                business_id=business_id,
                **payload.model_dump()
            )

            db.add(service)
            return commit_and_refresh(db, service)

        except HTTPException:
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Database error")

    @staticmethod
    def update_service(db: Session, service_id: UUID, user_id, payload):
        try:
            service = db.query(Service).filter(
                Service.id == service_id
            ).first()

            if not service or not service.is_active:
                raise HTTPException(404, "Service not found")

            check_service_owner(service, user_id)

            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(service, key, value)

            return commit_and_refresh(db, service)

        except HTTPException:
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Database error")

    @staticmethod
    def soft_delete(db: Session, service_id: UUID, user_id):
        try:
            service = db.query(Service).filter(
                Service.id == service_id
            ).first()

            if not service:
                raise HTTPException(404, "Service not found")

            check_service_owner(service, user_id)

            service.is_active = False
            commit_and_refresh(db, service)

            return {"message": "Service deleted successfully"}

        except HTTPException:
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Database error")