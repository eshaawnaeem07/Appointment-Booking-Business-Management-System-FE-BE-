from fastapi import HTTPException
from app.models.business import Business
from uuid import UUID, uuid5, NAMESPACE_DNS
from app.utils.constants import DAY_MAP, DAYS_LIST


def get_business_or_404(db, business_id: UUID):
    """Finds a business or raises 404."""
    
    business = (
        db.query(Business)
        .filter(Business.id == business_id)
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=404,
            detail="Business not found"
        )

    return business

def validate_time_logic(open_t, close_t, day_name: str = "this day"):
    """Validates that opening is before closing."""
    if open_t and close_t and open_t >= close_t:
        raise HTTPException(
            status_code=400, 
            detail=f"For {day_name}, open_time must be earlier than close_time."
        )

def format_time_str(t):
    """Safely formats time objects to string."""
    return t.strftime("%H:%M:%S") if t else None

def to_response_id(db_id):
    return uuid5(NAMESPACE_DNS, str(db_id))

def find_hour_by_uuid(hours_list, target_uuid: UUID):
    for h in hours_list:
        # Generate the pseudo-UUID from the DB integer and compare to the string from the URL
        if to_response_id(h.id) == target_uuid:
            return h
    return None
