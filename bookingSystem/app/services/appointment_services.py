from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.business import Business
from app.models.service import Service
from app.utils.appointment_utils import (
    ensure_appointment_not_completed,
    ensure_appointment_owner,
    ensure_appointment_status,
    ensure_business_is_open,
    ensure_can_view_appointment,
    ensure_slot_available,
    ensure_user_owns_appointment,
    get_appointment_or_404,
    is_business_owner,ensure_future_appointment,
    get_available_slots as generate_available_slots)
from app.utils.enums import AppointmentStatus
from app.workers.tasks import mark_no_show, mark_appointment_completed
from app.services.email_service import EmailService
from app.utils.customer_utils import get_customer_email
from app.utils.customer_utils import get_customer_or_404
from uuid import UUID
from datetime import timedelta, date, datetime, UTC

NO_SHOW_CONFIRMATION_WINDOW_SECONDS = 4 * 60 * 60

class AppointmentService:
    @staticmethod
    def get_my_appointments(db: Session, user):
        try:
            if is_business_owner(user):
                return db.query(Appointment).join(Service).join(Business).filter(
                    Business.owner_id == user.id
                ).all()

            return db.query(Appointment).filter(
                Appointment.user_id == user.id
            ).all()

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Failed to fetch appointments")

    @staticmethod
    def get_by_id(db: Session, appointment_id, user):
        try:
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_can_view_appointment(appointment, user)
            return appointment

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Failed to fetch appointment")

    @staticmethod
    def get_status(db: Session, appointment_id, user):
        try:
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_can_view_appointment(appointment, user)
            return {
                "appointment_id": appointment.id,
                "status": appointment.status,
            }

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Failed to fetch appointment status")

    @staticmethod
    def book_appointment(db: Session, user, payload):
        try:
            service = db.query(Service).filter(
                Service.id == payload.service_id,
                Service.is_active == True
            ).first()

            if not service:
                raise HTTPException(404, "Service not found")

            if service.business.is_deleted:
                raise HTTPException(404, "Business not found")

            # (future-safe check)
            if payload.walk_in_customer_id and user.id:
                pass

            walk_in_customer_id = None

            if payload.walk_in_customer_id:
                customer = get_customer_or_404(
                    db,
                    service.business_id,
                    payload.walk_in_customer_id,
                    user
                )
                walk_in_customer_id = customer.id


            start_time = payload.start_time
            end_time = start_time + timedelta(minutes=service.duration)

            ensure_future_appointment(start_time)

            ensure_business_is_open(db, service, start_time, end_time)
            ensure_slot_available(db, service, start_time, end_time)

            user_id = user.id
            walk_in_customer = None

            if payload.walk_in_customer_id:
                user_id = None
                walk_in_customer = walk_in_customer_id

            appointment = Appointment(
                user_id=user_id,
                walk_in_customer_id=walk_in_customer, 
                business_id=service.business_id,
                service_id=service.id,
                start_time=start_time,
                end_time=end_time,
                status=AppointmentStatus.PENDING,
            )

            db.add(appointment)
            db.commit()
            db.refresh(appointment)

            try:
                customer_email = get_customer_email(user, appointment)
                customer_name = (
                    appointment.walk_in_customer.name
                    if appointment.walk_in_customer
                    else user.email
                )

                EmailService.send_booking_confirmation_email(
                    customer_email,
                    customer_name,
                    service.name,
                    appointment.start_time,
                    appointment.end_time,
                    requires_deposit=service.requires_deposit,
                )
            except Exception as e:
                print("BOOKING CONFIRMATION EMAIL ERROR:", str(e))
            
            # If the user does not confirm within 4 hours of booking,
            # the Celery task will mark the appointment as no_show.
            try:
                task = mark_no_show.apply_async(
                    args=[str(appointment.id)],
                    countdown=NO_SHOW_CONFIRMATION_WINDOW_SECONDS,
                )
                print(f"[✓ CELERY SUCCESS] Task scheduled - Task ID: {task.id}, Appointment ID: {appointment.id}")
            except Exception as e:
                print(f"[✗ CELERY ERROR] Failed to schedule task: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

            return appointment

        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Failed to book appointment")
    
    @staticmethod
    def update_appointment(db: Session, appointment_id, user, payload):
        try:
            appointment = get_appointment_or_404(db, appointment_id)

            # Ensure user owns appointment
            ensure_user_owns_appointment(appointment, user)

            # Only pending appointments can be rescheduled
            ensure_appointment_status(
                appointment,
                AppointmentStatus.PENDING,
                "Only pending appointments can be rescheduled"
            )

            service = appointment.service

            new_start_time = payload.start_time
            new_end_time = new_start_time + timedelta(minutes=service.duration)

            # Prevent past booking
            ensure_future_appointment(new_start_time)

            # Business hours validation
            ensure_business_is_open(
                db,
                service,
                new_start_time,
                new_end_time
            )

            # Check conflicting appointments
            conflict = db.query(Appointment).filter(
                Appointment.business_id == service.business_id,
                Appointment.id != appointment.id,
                Appointment.start_time < new_end_time,
                Appointment.end_time > new_start_time,
                Appointment.status.in_([
                    AppointmentStatus.PENDING,
                    AppointmentStatus.CONFIRMED,
                ])
            ).first()

            if conflict:
                raise HTTPException(400, "Time slot already booked")

            # Update appointment
            appointment.start_time = new_start_time
            appointment.end_time = new_end_time

            db.commit()
            db.refresh(appointment)

            return appointment

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(500, "Failed to update appointment")
    @staticmethod
    def confirm_appointment(db: Session, appointment_id, user):
        try:
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_user_owns_appointment(appointment, user)
            ensure_appointment_status(
                appointment,
                AppointmentStatus.PENDING,
                "Only pending appointments can be confirmed"
            )

            appointment.status = AppointmentStatus.CONFIRMED
            db.commit()
            db.refresh(appointment)
            
            # Schedule task to mark appointment as completed at end_time
            try:
                if appointment.end_time:
                    now = datetime.now()
                    countdown_seconds = max(0, int((appointment.end_time - now).total_seconds()))
                    
                    if countdown_seconds > 0:
                        task = mark_appointment_completed.apply_async(
                            args=[str(appointment.id)],
                            countdown=countdown_seconds,
                        )
                        print(f"[✓ CELERY SUCCESS] Completion task scheduled - Task ID: {task.id}, Appointment ID: {appointment.id}, Scheduled for: {appointment.end_time}")
                    else:
                        print(f"[! CELERY INFO] Appointment {appointment.id} end_time is in the past, marking as completed immediately")
                        task = mark_appointment_completed.apply_async(
                            args=[str(appointment.id)],
                            countdown=0,
                        )
            except Exception as e:
                print(f"[✗ CELERY ERROR] Failed to schedule completion task: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
            
            return appointment

        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Failed to confirm appointment")

    @staticmethod
    def complete_appointment(db: Session, appointment_id, user):
        try:
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_appointment_owner(appointment, user)
            ensure_appointment_status(
                appointment,
                AppointmentStatus.CONFIRMED,
                "Only confirmed appointments can be completed"
            )

            appointment.status = AppointmentStatus.COMPLETED
            db.commit()
            db.refresh(appointment)

            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )
                EmailService.send_completion_email(
                    customer_email,
                    appointment.service.name,
                    appointment.end_time,
                )
            except Exception as e:
                print("COMPLETION EMAIL ERROR:", str(e))

            return appointment

        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Failed to complete appointment")

    @staticmethod
    def mark_no_show_manual(db: Session, appointment_id, user):
        try:
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_appointment_owner(appointment, user)
            ensure_appointment_not_completed(appointment)

            appointment.status = AppointmentStatus.NO_SHOW
            db.commit()
            db.refresh(appointment)

            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )
                EmailService.send_no_show_email(
                    customer_email,
                    appointment.service.name,
                    appointment.start_time,
                )
            except Exception as e:
                print("NO-SHOW EMAIL ERROR:", str(e))

            return appointment

        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise HTTPException(500, "Failed to mark appointment as no-show")

    @staticmethod
    
    def get_business_appointments(db: Session, business_id: UUID, user: UUID):
        try:
            business = db.query(Business).filter(
                Business.id == business_id,
                Business.owner_id == user.id
            ).first()

            if not business:
                raise HTTPException(403, "Not allowed")

            return db.query(Appointment).filter(
               Appointment.business_id == business_id
            ).all()

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Failed to fetch business appointments")
        
    @staticmethod
    def get_available_slots(
        db: Session,
        service_id: UUID,
        selected_date: date | None = None
    ):

        try:

            service = db.query(Service).filter(
                Service.id == service_id,
                Service.is_active == True
            ).first()

            if not service:
                raise HTTPException(
                    status_code=404,
                    detail="Service not found"
                )

            if service.business.is_deleted:
                raise HTTPException(
                    status_code=404,
                    detail="Business not found"
                )

            # Use today if no date provided
            if not selected_date:
                selected_date = datetime.now().date()

            days = []

            for i in range(15):

                current_date = selected_date + timedelta(days=i)

                slots = generate_available_slots(
                    db=db,
                    service=service,
                    selected_date=current_date
                )

                if slots:
                    days.append({
                        "date": current_date,
                        "available_slots": slots
                    })

            return {
                "days": days
            }

        except HTTPException:
            raise

        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch available slots"
            )
