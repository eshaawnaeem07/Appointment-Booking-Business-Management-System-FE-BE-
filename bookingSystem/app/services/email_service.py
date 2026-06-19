import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)


def _send_email_direct(to_email: str, subject: str, html_content: str):
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


class EmailService:
    @staticmethod
    def send_otp_email(email: str, otp: str):
        try:
            from app.workers.tasks import send_otp_email_task
            send_otp_email_task.delay(email, otp)

        except Exception as e:
            try:
                _send_email_direct(
                    email,
                    "Your Password Reset OTP",
                    f"<strong>Your OTP is: {otp}</strong>. It expires in 15 minutes.",
                )
            except Exception as direct_error:
                print("EMAIL ERROR:", str(direct_error))
                raise HTTPException(status_code=500, detail=f"Email failed: {str(direct_error)}")

    @staticmethod
    def send_booking_confirmation_email(
        email: str,
        customer_name: str,
        service_name: str,
        appointment_time,
        appointment_end_time,
        requires_deposit: bool = False,
    ):
        try:
            from app.workers.tasks import send_booking_confirmation_email_task
            send_booking_confirmation_email_task.delay(
                email,
                customer_name,
                service_name,
                appointment_time.isoformat(),
                appointment_end_time.isoformat(),
                requires_deposit,
            )

        except Exception as e:
            try:
                deposit_note = (
                    "<p>This service requires a deposit. Your appointment is reserved, but it will only be fully confirmed after payment is completed.</p>"
                    if requires_deposit
                    else "<p>Your appointment is confirmed.</p>"
                )
                _send_email_direct(
                    email,
                    "Appointment Booking Confirmation",
                    f"""
                    <h2>Appointment Booked</h2>
                    <p>Hello {customer_name or 'Customer'},</p>
                    <p>Thanks for booking with us. Here are your appointment details:</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    <p><strong>Start Time:</strong> {appointment_time.strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>End Time:</strong> {appointment_end_time.strftime('%Y-%m-%d %H:%M')}</p>
                    {deposit_note}
                    """,
                )
            except Exception as direct_error:
                print(f"Failed to send booking confirmation email: {str(direct_error)}")

    @staticmethod
    def send_payment_confirmation_email(email: str, service_name: str, appointment_time):
        try:
            from app.workers.tasks import send_payment_confirmation_email_task
            send_payment_confirmation_email_task.delay(
                email,
                service_name,
                appointment_time.isoformat(),
            )

        except Exception as e:
            try:
                _send_email_direct(
                    email,
                    "Payment Confirmed - Appointment Booking",
                    f"""
                    <h2>Payment Confirmation</h2>
                    <p>Your payment has been successfully received!</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    <p><strong>Appointment Time:</strong> {appointment_time.strftime('%Y-%m-%d %H:%M')}</p>
                    <p>Your appointment is now confirmed. Thank you for booking with us!</p>
                    """,
                )
            except Exception as direct_error:
                print(f"Failed to send payment confirmation email: {str(direct_error)}")

    @staticmethod
    def send_appointment_confirmed_email(email: str, service_name: str, appointment_time):
        try:
            _send_email_direct(
                email,
                "Your Appointment Is Confirmed",
                f"""
                <h2>Appointment Confirmed</h2>
                <p>Your appointment is now confirmed.</p>
                <p><strong>Service:</strong> {service_name}</p>
                <p><strong>Appointment Time:</strong> {appointment_time.strftime('%Y-%m-%d %H:%M')}</p>
                <p>We look forward to seeing you.</p>
                """,
            )

        except Exception as e:
            print(f"Failed to send appointment confirmation email: {str(e)}")

    @staticmethod
    def send_completion_email(email: str, service_name: str, appointment_time):
        try:
            from app.workers.tasks import send_completion_email_task
            send_completion_email_task.delay(
                email,
                service_name,
                appointment_time.isoformat(),
            )

        except Exception as e:
            try:
                _send_email_direct(
                    email,
                    "Appointment Completed",
                    f"""
                    <h2>Appointment Completed</h2>
                    <p>Your appointment has been marked as completed.</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    <p><strong>Appointment Time:</strong> {appointment_time.strftime('%Y-%m-%d %H:%M')}</p>
                    <p>Thank you for booking with us.</p>
                    """,
                )
            except Exception as direct_error:
                print(f"Failed to send completion email: {str(direct_error)}")

    @staticmethod
    def send_no_show_email(email: str, service_name: str, appointment_time):
        try:
            from app.workers.tasks import send_no_show_email_task
            send_no_show_email_task.delay(
                email,
                service_name,
                appointment_time.isoformat(),
            )

        except Exception as e:
            try:
                _send_email_direct(
                    email,
                    "Appointment Marked as No-Show",
                    f"""
                    <h2>Appointment No-Show</h2>
                    <p>Your appointment has been marked as no-show.</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    <p><strong>Appointment Time:</strong> {appointment_time.strftime('%Y-%m-%d %H:%M')}</p>
                    <p>If you still need this service, please book a new appointment.</p>
                    """,
                )
            except Exception as direct_error:
                print(f"Failed to send no-show email: {str(direct_error)}")

    @staticmethod
    def send_payment_request_email(email: str, customer_name: str, service_name: str, appointment_time, checkout_url: str):
        try:
            from app.workers.tasks import send_payment_request_email_task
            send_payment_request_email_task.delay(
                email,
                customer_name,
                service_name,
                appointment_time.isoformat(),
                checkout_url,
            )

        except Exception as e:
            try:
                _send_email_direct(
                    email,
                    "Complete Payment for Your Appointment",
                    f"""
                    <h2>Appointment Payment Required</h2>
                    <p>Hello {customer_name or 'Customer'},</p>
                    <p>Your appointment has been booked and a deposit payment is required.</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    <p><strong>Appointment Time:</strong> {appointment_time.strftime('%Y-%m-%d %H:%M')}</p>
                    <p><a href="{checkout_url}">Pay securely with Stripe</a></p>
                    <p>If the button does not open, copy this link into your browser:</p>
                    <p>{checkout_url}</p>
                    """,
                )
            except Exception as direct_error:
                print(f"Failed to send payment request email: {str(direct_error)}")

    @staticmethod
    def send_payment_failed_email(email: str, service_name: str):
        try:
            from app.workers.tasks import send_payment_failed_email_task
            send_payment_failed_email_task.delay(email, service_name)

        except Exception as e:
            try:
                _send_email_direct(
                    email,
                    "Payment Failed - Please Retry",
                    f"""
                    <h2>Payment Failed</h2>
                    <p>Unfortunately, your payment could not be processed.</p>
                    <p><strong>Service:</strong> {service_name}</p>
                    <p>Please try again with a different payment method or contact support if the problem persists.</p>
                    """,
                )
            except Exception as direct_error:
                print(f"Failed to send payment failed email: {str(direct_error)}")
