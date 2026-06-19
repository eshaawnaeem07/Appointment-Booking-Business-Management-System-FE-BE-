from fastapi import HTTPException


def check_business_owner(business, user_id):
    if business.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

def check_service_owner(service, user_id):
    if service.business.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not Allowed")
    
