from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from app.services.booking_service import ServiceService
from app.core.dependencies import get_current_user, require_roles
from app.utils.enums import UserRole
from uuid import UUID

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/businesses/{business_id}/services", response_model=list[ServiceOut])
def get_business_services(business_id: UUID, db: Session = Depends(get_db)):
    try:
        return ServiceService.get_by_business(db, business_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch services: {str(e)}"
        )

@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: UUID, db: Session = Depends(get_db)):
    try:
        service = ServiceService.get_by_id(db, service_id)

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        return service

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching service: {str(e)}"
        )

@router.post(
    "/businesses/{business_id}/services",
    response_model=ServiceOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.BUSINESS))]
)
def create_service(
    business_id: UUID,
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return ServiceService.create_service(db, business_id, user.id, payload)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating service: {str(e)}")

@router.put("/services/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return ServiceService.update_service(db, service_id, user.id, payload)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating service: {str(e)}"
        )


@router.delete("/services/{service_id}")
def delete_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return ServiceService.soft_delete(db, service_id, user.id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting service: {str(e)}"
        )