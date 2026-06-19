from datetime import datetime
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.business_hours import BusinessHours
from app.models.service import Service
from app.utils.enums import AppointmentStatus, UserRole
from datetime import timedelta

#check if user is business owner
def is_business_owner(user):
    return user.role == UserRole.BUSINESS.value

# Get appointment or raise 404
def get_appointment_or_404(db: Session, appointment_id: UUID):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(404, "Appointment not found")

    return appointment

# Ensure user can view appointment
def ensure_can_view_appointment(appointment: Appointment, user):
    if appointment.user_id == user.id:
        return

    if appointment.service and appointment.service.business.owner_id == user.id:
        return

    raise HTTPException(403, "Not allowed")

# Ensure user is owner of appointment's business
def ensure_appointment_owner(appointment: Appointment, user):
    if not appointment.service or appointment.service.business.owner_id != user.id:
        raise HTTPException(403, "Not allowed")

# Ensure user owns the appointment
def ensure_user_owns_appointment(appointment: Appointment, user):
    if appointment.user_id != user.id:
        raise HTTPException(403, "Not allowed")

# Ensure appointment is in expected status
def ensure_appointment_status(appointment: Appointment, expected_status: AppointmentStatus, message: str):
    if appointment.status != expected_status:
        raise HTTPException(400, message)

# Ensure appointment is not completed before marking no-show
def ensure_appointment_not_completed(appointment: Appointment):
    if appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(400, "Completed appointments cannot be marked no-show")

# Convert business_id to UUID if possible, otherwise return as string
def business_hours_id(business_id: str):
    try:
        return UUID(str(business_id))
    except ValueError:
        return business_id

# Ensure business is open at the requested time
def ensure_business_is_open(
    db: Session,
    service: Service,
    start_time: datetime,
    end_time: datetime
):
    if start_time >= end_time:
        raise HTTPException(400, "Invalid appointment time")

    if start_time.date() != end_time.date():
        raise HTTPException(400, "Appointment must start and end on the same day")

    hours = db.query(BusinessHours).filter(
        BusinessHours.business_id == business_hours_id(service.business_id),
        BusinessHours.day_of_week == start_time.weekday(),
        BusinessHours.is_open == True
    ).first()

    if not hours:
        raise HTTPException(400, "Business is closed at this time")

    if start_time.time() < hours.open_time or end_time.time() > hours.close_time:
        raise HTTPException(400, "Appointment must be within business hours")

# Ensure no conflicting appointments exist for the requested time slot
def ensure_slot_available(
    db: Session,
    service: Service,
    start_time: datetime,
    end_time: datetime
):
    conflict = db.query(Appointment).filter(
        Appointment.business_id == service.business_id,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
        Appointment.status.in_([
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED,
        ])
    ).first()

    if conflict:
        raise HTTPException(400, "Time slot already booked")
    
# Ensure appointment is not booked in the past
def ensure_future_appointment(start_time: datetime):
    current_time = datetime.now()

    if start_time < current_time:
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointment of the past. Please select a future time."
        )
# Generate available slots for a service
def get_available_slots(
    db: Session,
    service: Service,
    selected_date
):
    """
    Returns available slots for a service on a specific date.
    """

    # Find business hours for selected day
    hours = db.query(BusinessHours).filter(
        BusinessHours.business_id == business_hours_id(service.business_id),
        BusinessHours.day_of_week == selected_date.weekday(),
        BusinessHours.is_open == True
    ).first()
    
    # Business closed
    if not hours:
        return []

    # service_duration = timedelta(minutes=service.duration_minutes)
    service_duration = timedelta(minutes=service.duration)
    # Build opening datetime
    current_slot = datetime.combine(
        selected_date,
        hours.open_time
    )

    closing_datetime = datetime.combine(
        selected_date,
        hours.close_time
    )

    available_slots = []

    while current_slot + service_duration <= closing_datetime:

        slot_end = current_slot + service_duration

        try:
            # Validate future booking
            ensure_future_appointment(current_slot)

            # Validate within business hours
            ensure_business_is_open(
                db,
                service,
                current_slot,
                slot_end
            )

            # Validate slot availability
            ensure_slot_available(
                db,
                service,
                current_slot,
                slot_end
            )

            # If no exception -> slot is available
            available_slots.append(current_slot)

        except HTTPException:
            pass

        # Move to next slot
        current_slot += service_duration

    return available_slots
