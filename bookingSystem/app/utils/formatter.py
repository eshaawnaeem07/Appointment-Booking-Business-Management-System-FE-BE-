from app.utils.helpers import DAYS_LIST, format_time_str

def format_hour_response(h):
    return {
        "id": h.id,
        "business_id": h.business_id,
        "day_of_week": DAYS_LIST[h.day_of_week] if isinstance(h.day_of_week, int) else h.day_of_week,
        "is_open": h.is_open,
        "open_time": format_time_str(h.open_time) if h.is_open else None,
        "close_time": format_time_str(h.close_time) if h.is_open else None
    }
