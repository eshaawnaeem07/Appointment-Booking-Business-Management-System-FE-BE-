from fastapi import HTTPException
from app.models.business_customer import BusinessCustomer
from app.models.business import Business

def get_customer_or_404(db, business_id, customer_id, user):
    customer = db.query(BusinessCustomer).join(Business).filter(
        BusinessCustomer.id == customer_id,
        BusinessCustomer.business_id == business_id,
        Business.owner_id == user.id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer

# Utility function to get customer email for payment processing
def get_customer_email(user, appointment):
    email = appointment.walk_in_customer.email if appointment.walk_in_customer else user.email

    if not email:
        raise HTTPException(400, "Customer email not found")

    return email
