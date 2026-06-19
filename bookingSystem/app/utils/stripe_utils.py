import stripe
def create_stripe_checkout_session(
    customer_email,
    amount_cents,
    service,
    success_url,
    cancel_url,
    appointment_id,
    user_id
):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=customer_email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": service.name,
                        "description": service.description,
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "appointment_id": str(appointment_id),
            "user_id": str(user_id) if user_id else "",
        }
    )
