from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.payment import (
    PaymentCreateSession,
    PaymentOut,
    PaymentStatusResponse,
    CheckoutSessionResponse
)
from app.services.payment_service import PaymentService
from uuid import UUID

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Stripe checkout session for deposit",
    description="Create a Stripe checkout session for appointment deposit payment. Requires JWT authentication."
)
def create_checkout_session(
    payload: PaymentCreateSession,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    success_url: str = "http://localhost:3000/payment-success",
    cancel_url: str = "http://localhost:3000/payment-cancel"
):
    """
    Create Stripe checkout session for deposit
    
    Required:
    - appointment_id: ID of the appointment
    
    Query parameters:
    - success_url: URL to redirect after successful payment
    - cancel_url: URL to redirect if payment is cancelled
    
    Returns:
    - session_id: Stripe session ID
    - checkout_url: URL to redirect user for payment
    - payment_id: Payment record ID
    """
    try:
        return PaymentService.create_checkout_session(
            db,
            user,
            payload.appointment_id,
            success_url,
            cancel_url
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post(
    "/checkout-session",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Stripe checkout session",
    include_in_schema=False
)
def create_checkout_session_alias(
    payload: PaymentCreateSession,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    success_url: str = "http://localhost:5173/payment/success",
    cancel_url: str = "http://localhost:5173/payment/cancel"
):
    return create_checkout_session(payload, db, user, success_url, cancel_url)


@router.get(
    "/{appointment_id}",
    response_model=PaymentOut,
    summary="Get payment record for an appointment",
    description="Get payment record details for a specific appointment. Requires JWT authentication."
)
def get_payment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        return PaymentService.get_payment_by_appointment(db, user, appointment_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch payment: {str(e)}"
        )


@router.get(
    "/{appointment_id}/status",
    response_model=PaymentStatusResponse,
    summary="Get current payment status",
    description="Get current payment status for an appointment. Requires JWT authentication."
)
def get_payment_status(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        return PaymentService.get_payment_status(db, user, appointment_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch payment status: {str(e)}"
        )


@router.get(
    "/appointments/{appointment_id}/status",
    response_model=PaymentStatusResponse,
    include_in_schema=False
)
def get_payment_status_alias(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return get_payment_status(appointment_id, db, user)


@router.post(
    "/webhook",
    summary="Stripe webhook handler",
    description="Receive and process Stripe webhook events for payment status updates. No authentication required."
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Get payload and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=400,
                detail="Missing Stripe signature header"
            )
        
        # Verify webhook signature
        is_valid, event = PaymentService.verify_webhook_signature(payload, sig_header)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid Stripe signature"
            )
        
        # Handle the event
        result = PaymentService.handle_stripe_webhook(event, db)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}"
        )

