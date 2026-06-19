from datetime import time
from datetime import datetime
from fastapi import HTTPException
def normalize_time(v):
    if v is None:
        return None

    if isinstance(v, time):
        return v

    v = str(v)

    parts = v.split(":")

    if len(parts) == 1:
        return time(int(parts[0]), 0)

    if len(parts) == 2:
        return time(int(parts[0]), int(parts[1]))

    if len(parts) == 3:
        return time(int(parts[0]), int(parts[1]), int(parts[2]))

    raise ValueError("Invalid time format")

def validate_date_format(selected_date: str):

    try:
        return datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail='Please enter date in format "YYYY-MM-DD"'
        )