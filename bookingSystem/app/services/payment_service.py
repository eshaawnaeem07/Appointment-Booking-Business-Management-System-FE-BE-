import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.core.config import settings
from app.utils.enums import PaymentStatus, AppointmentStatus
from app.utils.appointment_utils import get_appointment_or_404, ensure_can_view_appointment
from app.services.email_service import EmailService
from app.utils.payment_utils import (
    get_payment_by_appointment as db_get_payment_by_appointment,
    get_payment_by_session_id
)
from app.utils.stripe_utils import create_stripe_checkout_session
from app.utils.customer_utils import get_customer_email
from uuid import UUID

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    @staticmethod
    def create_checkout_session(db: Session, user, appointment_id: UUID, success_url: str, cancel_url: str):
        try:
            # Verify appointment exists
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_can_view_appointment(appointment, user)
            
            # Get service details
            service = appointment.service
            if not service:
                raise HTTPException(404, "Service not found")
            
            # Check if deposit is required
            if not service.requires_deposit:
                raise HTTPException(400, "This service does not require a deposit")
            
            # Check if payment already exists
            existing_payment = db.query(Payment).filter(
                Payment.appointment_id == appointment_id
            ).first()

            # Already paid
            if existing_payment and existing_payment.status == PaymentStatus.PAID:
                raise HTTPException(400,"Payment already completed for this appointment")

            # Pending payments can receive a fresh checkout link.
            # This is useful when a business sends or resends payment URLs to walk-in/call customers.
            # Calculate amount (convert dollars to cents for Stripe)
            amount_cents = int(service.price * 100)
            
            # Get customer email
            customer_email = get_customer_email(user, appointment)
            
            session = create_stripe_checkout_session(
                customer_email=customer_email,
                amount_cents=amount_cents,
                service=service,
                success_url=success_url,
                cancel_url=cancel_url,
                appointment_id=appointment_id,
                user_id=user.id if user.id else None
            )
            # Create or update payment record
            if existing_payment:
                existing_payment.stripe_session_id = session.id
                existing_payment.amount = amount_cents
                existing_payment.status = PaymentStatus.PENDING
                db.commit()
                db.refresh(existing_payment)
                payment = existing_payment
            else:
                payment = Payment(
                    appointment_id=appointment_id,
                    stripe_session_id=session.id,
                    amount=amount_cents,
                    status=PaymentStatus.PENDING
                )
                db.add(payment)
                db.commit()
                db.refresh(payment)

            try:
                EmailService.send_payment_request_email(
                    customer_email,
                    appointment.walk_in_customer.name if appointment.walk_in_customer else user.email,
                    service.name,
                    appointment.start_time,
                    session.url
                )
            except Exception as e:
                print("PAYMENT REQUEST EMAIL ERROR:", str(e))
            
            return {
                "session_id": session.id,
                "checkout_url": session.url,
                "payment_id": payment.id
            }
        
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Failed to create checkout session: {str(e)}")

    @staticmethod
    def get_payment_by_appointment(db: Session, user, appointment_id: UUID):
        try:
            # Verify appointment exists and user can access
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_can_view_appointment(appointment, user)
            
            # Get payment record
            payment = db_get_payment_by_appointment(db,appointment_id)
            
            if not payment:
                raise HTTPException(404, "No payment record found for this appointment")

            PaymentService.sync_payment_from_stripe(db, payment)
            
            return payment
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Failed to fetch payment: {str(e)}")

    @staticmethod
    def get_payment_status(db: Session, user, appointment_id: UUID):
        try:
            # Verify appointment exists and user can access
            appointment = get_appointment_or_404(db, appointment_id)
            ensure_can_view_appointment(appointment, user)
            
            # Get payment record
            payment = db_get_payment_by_appointment(db,appointment_id)
            
            if not payment:
                raise HTTPException(404, "No payment record found for this appointment")

            PaymentService.sync_payment_from_stripe(db, payment)
            
            return payment
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Failed to fetch payment status: {str(e)}")

    @staticmethod
    def handle_stripe_webhook(event, db: Session):
        try:
            event_type = event["type"]

            print("Webhook event:", event_type)

            if event_type == "checkout.session.completed":
                session = event["data"]["object"]

                return PaymentService._handle_successful_payment(db,session)

            elif event_type == "checkout.session.async_payment_failed":
                session = event["data"]["object"]

                return PaymentService._handle_failed_payment(db,session)

            return {
                "status": "ignored",
                "event": event_type
            }

        except Exception as e:
            db.rollback()
            print("Webhook error:", str(e))
            raise HTTPException(
                status_code=500,
                detail=f"Webhook failed: {str(e)}"
            )

    @staticmethod
    def _handle_successful_payment(db: Session, session_data):
        try:
            # Stripe session object
            session_id = session_data.id
            payment_intent_id = session_data.payment_intent

            print("SESSION ID:", session_id)
            print("PAYMENT INTENT:", payment_intent_id)

            # Find payment in DB
            payment = get_payment_by_session_id(db,session_id)
            print("PAYMENT FOUND:", payment)

            if not payment:
                raise Exception(
                    f"Payment not found for session {session_id}"
                )

            # Already processed
            if payment.status == PaymentStatus.PAID:
                return {
                    "status": "already_processed"
                }

            # Get appointment
            appointment = db.query(Appointment).filter(
                Appointment.id == payment.appointment_id
            ).first()

            if not appointment:
                raise Exception("Appointment not found")

            # Update payment
            payment.status = PaymentStatus.PAID
            payment.stripe_payment_intent = payment_intent_id

            # Update appointment
            appointment.status = AppointmentStatus.CONFIRMED

            # Save DB
            db.commit()

            db.refresh(payment)
            db.refresh(appointment)

            print("PAYMENT UPDATED SUCCESSFULLY")

            # Send email
            try:
                customer_email = (
                    appointment.user.email
                    if appointment.user
                    else appointment.walk_in_customer.email
                )

                EmailService.send_payment_confirmation_email(
                    customer_email,
                    appointment.service.name,
                    appointment.start_time
                )

            except Exception as e:
                print("EMAIL ERROR:", str(e))

            return {
                "status": "success",
                "payment_id": payment.id}

        except Exception as e:
            db.rollback()
            print("SUCCESS PAYMENT ERROR:", str(e))
            raise
    @staticmethod
    def _handle_failed_payment(db: Session, session_data):
        try:
            session_id = session_data.id

            payment = get_payment_by_session_id(db,session_id)

            if not payment:
                raise Exception("Payment not found")

            if payment.status == PaymentStatus.FAILED:
                return {"status": "already_failed"}

            payment.status = PaymentStatus.FAILED

            db.commit()
            db.refresh(payment)

            return {
                "status": "failed",
                "payment_id": payment.id
            }

        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def sync_payment_from_stripe(db: Session, payment: Payment):
        """
        Keep local payment status updated when webhooks are not running locally.
        Webhooks should still be used in production, but this makes GET/status
        reflect Stripe after the customer returns from Checkout.
        """
        if not payment or payment.status != PaymentStatus.PENDING or not payment.stripe_session_id:
            return payment

        try:
            session = stripe.checkout.Session.retrieve(
                payment.stripe_session_id,
                expand=["payment_intent"]
            )
            payment_intent = getattr(session, "payment_intent", None)
            payment_intent_id = (
                getattr(payment_intent, "id", None)
                if not isinstance(payment_intent, str)
                else payment_intent
            )
            payment_intent_status = (
                getattr(payment_intent, "status", None)
                if not isinstance(payment_intent, str)
                else None
            )
            payment_status = getattr(session, "payment_status", None)
            session_status = getattr(session, "status", None)

            if payment_status == "paid":
                appointment = db.query(Appointment).filter(
                    Appointment.id == payment.appointment_id
                ).first()

                was_pending = payment.status == PaymentStatus.PENDING
                payment.status = PaymentStatus.PAID
                payment.stripe_payment_intent = payment_intent_id

                if appointment:
                    appointment.status = AppointmentStatus.CONFIRMED

                db.commit()
                db.refresh(payment)
                if appointment:
                    db.refresh(appointment)

                if was_pending and appointment:
                    try:
                        customer_email = (
                            appointment.user.email
                            if appointment.user
                            else appointment.walk_in_customer.email
                        )

                        EmailService.send_payment_confirmation_email(
                            customer_email,
                            appointment.service.name,
                            appointment.start_time,
                        )
                        EmailService.send_appointment_confirmed_email(
                            customer_email,
                            appointment.service.name,
                            appointment.start_time,
                        )

                    except Exception as e:
                        print("EMAIL ERROR:", str(e))

                return payment

            failed_intent_statuses = {
                "canceled",
                "requires_payment_method",
            }

            if session_status == "expired" or payment_intent_status in failed_intent_statuses:
                payment.status = PaymentStatus.FAILED
                payment.stripe_payment_intent = payment_intent_id
                db.commit()
                db.refresh(payment)

            return payment

        except Exception as e:
            db.rollback()
            print(f"Stripe payment sync failed: {str(e)}")
            return payment

    @staticmethod
    def verify_webhook_signature(payload, sig_header):
        """
        Verify Stripe webhook signature
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return True, event
        except ValueError:
            print("Invalid signature - ValueError")
            return False, None
        except Exception as e:
            print(f"Webhook verification failed: {str(e)}")
            return False, None
