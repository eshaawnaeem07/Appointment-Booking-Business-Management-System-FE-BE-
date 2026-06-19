from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.business_hours import BusinessHourCreate, BusinessHourUpdate
from app.services.business_hours_service import BusinessHoursService
from app.core.dependencies import get_current_user, require_roles
from app.utils.enums import UserRole
from uuid import UUID
from app.schemas.business_hours import BusinessHourOut

router = APIRouter(prefix="/businesses", tags=["Business Hours"])


# GET BUSINESS HOURS
@router.get("/{id}/hours")
def get_hours(id: UUID, db: Session = Depends(get_db)):
    try:
        return BusinessHoursService.get_hours(db, id)
    except HTTPException as e:
        raise e
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# SET BUSINESS HOURS
@router.post("/{id}/hours", response_model=list[BusinessHourOut])
def set_hours(
    id: UUID,  
    hours: list[BusinessHourCreate],
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _ = Depends(require_roles(UserRole.BUSINESS))
):
    # Call the service
    return BusinessHoursService.set_hours(db, id, hours, user.id)

# UPDATE SPECIFIC HOUR
@router.put("/{id}/hours/{hour_id}")
def update_hour(
    id: UUID,
    hour_id: UUID,
    data: BusinessHourUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _: bool = Depends(require_roles(UserRole.BUSINESS))
):
    try:
        return BusinessHoursService.update_hour(
            db,
            id,
            hour_id,
            data,
            user.id
        )

    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )