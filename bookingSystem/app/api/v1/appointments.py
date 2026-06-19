from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentOut,
    AppointmentStatusResponse,
    AvailableSlotsResponse, AvailableSlotsRangeResponse
)
from app.db.session import get_db
from app.services.appointment_services import AppointmentService
from app.core.dependencies import get_current_user
from uuid import UUID
from datetime import date
from app.utils.validators import validate_date_format

router = APIRouter(tags=["Appointments"])
# Get my appointments
@router.get("/appointments", response_model=list[AppointmentOut])
def get_my_appointments(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        return AppointmentService.get_my_appointments(db, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch appointments: {str(e)}"
        )
# Get appointment by ID
@router.get("/appointments/{id}", response_model=AppointmentOut)
def get_appointment(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AppointmentService.get_by_id(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch appointment: {str(e)}"
        )

@router.get("/appointments/{id}/status", response_model=AppointmentStatusResponse)
def get_appointment_status(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AppointmentService.get_status(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch appointment status: {str(e)}"
        )
# Book appointment
@router.post(
    "/appointments",
    response_model=AppointmentOut,
    status_code=status.HTTP_201_CREATED
)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        return AppointmentService.book_appointment(db, user, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to book appointment: {str(e)}"
        )
# Update appointment (reschedule)
@router.patch("/appointments/{id}", response_model=AppointmentOut)
def update_appointment(
    id: UUID,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        return AppointmentService.update_appointment(
            db,
            id,
            user,
            payload
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update appointment: {str(e)}"
        )
    
@router.patch("/appointments/{id}/confirm", response_model=AppointmentOut)
def confirm(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AppointmentService.confirm_appointment(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to confirm appointment: {str(e)}"
        )

@router.patch("/appointments/{id}/complete", response_model=AppointmentOut)
def complete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AppointmentService.complete_appointment(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete appointment: {str(e)}"
        )

@router.patch("/appointments/{id}/no-show", response_model=AppointmentOut)
def no_show(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AppointmentService.mark_no_show_manual(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark appointment as no-show: {str(e)}"
        )

@router.get("/businesses/{id}/appointments", response_model=list[AppointmentOut])
def business_appointments(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return AppointmentService.get_business_appointments(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch business appointments: {str(e)}"
        )

# Get available slots for a service
@router.get(
    "/services/{service_id}/available-slots",
    response_model=AvailableSlotsRangeResponse
)
def get_available_slots(
    service_id: UUID,
    selected_date: str | None = None,
    db: Session = Depends(get_db)
):
    try:

        parsed_date = None

        if selected_date:
            parsed_date = validate_date_format(selected_date)

        return AppointmentService.get_available_slots(
            db,
            service_id,
            parsed_date
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch available slots: {str(e)}"
        )
