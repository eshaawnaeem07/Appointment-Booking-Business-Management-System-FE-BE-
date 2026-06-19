from fastapi import HTTPException
from app.models.business import Business

def get_owned_business_or_403(db, business_id, user):
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == user.id
    ).first()

    if not business:
        raise HTTPException(status_code=403, detail="Not allowed")

    return business