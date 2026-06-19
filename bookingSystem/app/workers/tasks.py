import os
from pathlib import Path

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import Appointment
from app.utils.enums import AppointmentStatus
from uuid import UUID
from datetime import datetime, timedelta


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)


def _send_email(to_email: str, subject: str, html_content: str):
    api_key = os.getenv("SENDGRID_API_KEY", "").strip().strip('"').strip("'")
    from_email = os.getenv("FROM_EMAIL", "").strip().strip('"').strip("'")

    if not api_key or not from_email:
        raise Exception("Missing SendGrid configuration")

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)

    if response.status_code >= 400:
        raise Exception(f"SendGrid error: {response.status_code}")


def _parse_dt(value: str):
    return datetime.fromisoformat(value) if isinstance(value, str) else value


@celery_app.task(name='app.workers.tasks.send_otp_email_task')
def send_otp_email_task(email: str, otp: str):
    _send_email(
        email,
        "Your Password Reset OTP",
        f"<strong>Your OTP is: {otp}</strong>. It expires in 15 minutes.",
    )


@celery_app.task(name='app.workers.tasks.send_booking_confirmation_email_task')
def send_booking_confirmation_email_task(
    email: str,
    customer_name: str,
    service_name: str,
    appointment_time: str,
    appointment_end_time: str,
    requires_deposit: bool = False,
):
    deposit_note = (
        "<p>This service requires a deposit. Your appointment is reserved, but it will only be fully confirmed after payment is completed.</p>"
        if requires_deposit
        else "<p>Your appointment is confirmed.</p>"
    )
    start_time = _parse_dt(appointment_time)
    end_time = _parse_dt(appointment_end_time)

    _send_email(
        email,
        "Appointment Booking Confirmation",
        f"""
        <h2>Appointment Booked</h2>
        <p>Hello {customer_name or 'Customer'},</p>
        <p>Thanks for booking with us. Here are your appointment details:</p>
        <p><strong>Service:</strong> {service_name}</p>
        <p><strong>Start Time:</strong> {start_time.strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>End Time:</strong> {end_time.strftime('%Y-%m-%d %H:%M')}</p>
        {deposit_note}
        """,
    )


@celery_app.task(name='app.workers.tasks.send_payment_confirmation_email_task')
def send_payment_confirmation_email_task(email: str, service_name: str, appointment_time: str):
    _send_email(
        email,
        "Payment Confirmed - Appointment Booking",
        f"""
        <h2>Payment Confirmation</h2>
        <p>Your payment has been successfully received!</p>
        <p><strong>Service:</strong> {service_name}</p>
        <p><strong>Appointment Time:</strong> {_parse_dt(appointment_time).strftime('%Y-%m-%d %H:%M')}</p>
        <p>Your appointment is now confirmed. Thank you for booking with us!</p>
        """,
    )


@celery_app.task(name='app.workers.tasks.send_completion_email_task')
def send_completion_email_task(email: str, service_name: str, appointment_time: str):
    _send_email(
        email,
        "Appointment Completed",
        f"""
        <h2>Appointment Completed</h2>
        <p>Your appointment has been marked as completed.</p>
        <p><strong>Service:</strong> {service_name}</p>
        <p><strong>Appointment Time:</strong> {_parse_dt(appointment_time).strftime('%Y-%m-%d %H:%M')}</p>
        <p>Thank you for booking with us.</p>
        """,
    )


@celery_app.task(name='app.workers.tasks.send_no_show_email_task')
def send_no_show_email_task(email: str, service_name: str, appointment_time: str):
    _send_email(
        email,
        "Appointment Marked as No-Show",
        f"""
        <h2>Appointment No-Show</h2>
        <p>Your appointment has been marked as no-show.</p>
        <p><strong>Service:</strong> {service_name}</p>
        <p><strong>Appointment Time:</strong> {_parse_dt(appointment_time).strftime('%Y-%m-%d %H:%M')}</p>
        <p>If you still need this service, please book a new appointment.</p>
        """,
    )


@celery_app.task(name='app.workers.tasks.send_payment_request_email_task')
def send_payment_request_email_task(
    email: str,
    customer_name: str,
    service_name: str,
    appointment_time: str,
    checkout_url: str,
):
    _send_email(
        email,
        "Complete Payment for Your Appointment",
        f"""
        <h2>Appointment Payment Required</h2>
        <p>Hello {customer_name or 'Customer'},</p>
        <p>Your appointment has been booked and a deposit payment is required.</p>
        <p><strong>Service:</strong> {service_name}</p>
        <p><strong>Appointment Time:</strong> {_parse_dt(appointment_time).strftime('%Y-%m-%d %H:%M')}</p>
        <p><a href="{checkout_url}">Pay securely with Stripe</a></p>
        <p>If the button does not open, copy this link into your browser:</p>
        <p>{checkout_url}</p>
        """,
    )


@celery_app.task(name='app.workers.tasks.send_payment_failed_email_task')
def send_payment_failed_email_task(email: str, service_name: str):
    _send_email(
        email,
        "Payment Failed - Please Retry",
        f"""
        <h2>Payment Failed</h2>
        <p>Unfortunately, your payment could not be processed.</p>
        <p><strong>Service:</strong> {service_name}</p>
        <p>Please try again with a different payment method or contact support if the problem persists.</p>
        """,
    )


@celery_app.task(bind=True, name='app.workers.tasks.mark_no_show')
def mark_no_show(self, appointment_id: str):
    """Mark appointment as no_show if not confirmed within 4 hours"""
    print(f"[TASK STARTED] mark_no_show for appointment {appointment_id}")
    db = SessionLocal()

    try:
        # Convert string back to UUID
        appointment = db.query(Appointment).filter(
            Appointment.id == UUID(appointment_id)
        ).first()

        if appointment and appointment.status == AppointmentStatus.PENDING:
            appointment.status = AppointmentStatus.NO_SHOW
            db.commit()
            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )
                send_no_show_email_task.delay(
                    customer_email,
                    appointment.service.name,
                    appointment.start_time.isoformat(),
                )
            except Exception as e:
                print(f"[TASK EMAIL ERROR] Failed to queue no-show email: {type(e).__name__}: {e}")
            print(f"[✓ TASK SUCCESS] Appointment {appointment_id} marked as NO_SHOW")
            return {"status": "success", "appointment_id": appointment_id}
        else:
            print(f"[! TASK SKIPPED] Appointment {appointment_id} not found or already processed")
            return {"status": "skipped", "appointment_id": appointment_id}
    except Exception as e:
        print(f"[✗ TASK ERROR] Error marking appointment as no-show: {type(e).__name__}: {e}")
        # Don't raise - task completed but with info
        return {"status": "error", "appointment_id": appointment_id, "error": str(e)}
    finally:
        db.close()

# Celery task to auto-complete appointments that have passed their end_time
@celery_app.task(name='app.workers.tasks.mark_overdue_no_shows')
def mark_overdue_no_shows():
    """Recover pending appointments whose no-show delay already passed."""
    db = SessionLocal()

    try:
        cutoff = datetime.now() - timedelta(hours=4)
        appointments = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.PENDING,
            Appointment.start_time <= cutoff
        ).all()

        for appointment in appointments:
            appointment.status = AppointmentStatus.NO_SHOW
            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )
                send_no_show_email_task.delay(
                    customer_email,
                    appointment.service.name,
                    appointment.start_time.isoformat(),
                )
            except Exception as e:
                print(f"[TASK EMAIL ERROR] Failed to queue no-show email: {type(e).__name__}: {e}")

        db.commit()
        print(f"[TASK SUCCESS] Marked {len(appointments)} overdue appointments as NO_SHOW")
        return {"status": "success", "count": len(appointments)}
    except Exception as e:
        db.rollback()
        print(f"[TASK ERROR] Error marking overdue no-shows: {type(e).__name__}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

# Celery task to auto-complete appointments that have passed their end_time
@celery_app.task(bind=True, name='app.workers.tasks.mark_appointment_completed')
def mark_appointment_completed(self, appointment_id: str):
    """Mark appointment as completed after end_time"""
    print(f"[TASK STARTED] mark_appointment_completed for appointment {appointment_id}")
    db = SessionLocal()

    try:
        appointment = db.query(Appointment).filter(
            Appointment.id == UUID(appointment_id)
        ).first()

        if not appointment:
            print(f"[! TASK SKIPPED] Appointment {appointment_id} not found")
            return {"status": "skipped", "appointment_id": appointment_id, "reason": "not_found"}

        # Only mark as completed if status is confirmed or pending
        if appointment.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]:
            appointment.status = AppointmentStatus.COMPLETED
            db.commit()
            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )
                send_completion_email_task.delay(
                    customer_email,
                    appointment.service.name,
                    appointment.end_time.isoformat(),
                )
            except Exception as e:
                print(f"[TASK EMAIL ERROR] Failed to queue completion email: {type(e).__name__}: {e}")
            print(f"[✓ TASK SUCCESS] Appointment {appointment_id} marked as COMPLETED")
            return {"status": "success", "appointment_id": appointment_id}
        else:
            print(f"[! TASK SKIPPED] Appointment {appointment_id} status is {appointment.status}, cannot mark as completed")
            return {"status": "skipped", "appointment_id": appointment_id, "reason": f"status_is_{appointment.status}"}
    except Exception as e:
        print(f"[✗ TASK ERROR] Error marking appointment as completed: {type(e).__name__}: {e}")
        return {"status": "error", "appointment_id": appointment_id, "error": str(e)}
    finally:
        db.close()

# Celery task to auto-complete appointments that have passed their end_time
@celery_app.task(name='app.workers.tasks.auto_complete_past_appointments')
def auto_complete_past_appointments():
    """task to auto-complete appointments whose end_time has passed"""
    db = SessionLocal()

    try:
        now = datetime.now()
        
        # Find all confirmed appointments that have passed their end_time
        past_appointments = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.CONFIRMED,
            Appointment.end_time <= now
        ).all()

        count = 0
        for appointment in past_appointments:
            appointment.status = AppointmentStatus.COMPLETED
            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )
                send_completion_email_task.delay(
                    customer_email,
                    appointment.service.name,
                    appointment.end_time.isoformat(),
                )
            except Exception as e:
                print(f"[TASK EMAIL ERROR] Failed to queue completion email: {type(e).__name__}: {e}")
            count += 1

        db.commit()
        print(f"[✓ TASK SUCCESS] Auto-completed {count} past appointments")
        return {"status": "success", "count": count}
    except Exception as e:
        db.rollback()
        print(f"[✗ TASK ERROR] Error auto-completing appointments: {type(e).__name__}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

