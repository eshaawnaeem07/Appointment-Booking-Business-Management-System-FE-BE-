from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.payment import Payment


def get_payment_by_appointment(db: Session, appointment_id: UUID):
    return db.query(Payment).filter(
        Payment.appointment_id == appointment_id
    ).first()


def get_payment_by_session_id(db: Session, session_id: str):
    return db.query(Payment).filter(
        Payment.stripe_session_id == session_id
    ).first()


def get_payment_or_404(db: Session, payment_id: UUID):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment
