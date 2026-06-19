from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.business_hours import BusinessHours
from app.utils.helpers import (get_business_or_404, validate_time_logic)
from app.utils.validators import normalize_time
from app.utils.auth_utils import check_business_owner
from app.utils.db_utils import commit_and_refresh
from app.utils.formatter import format_hour_response
from app.utils.constants import DAY_MAP, DAYS_LIST
class BusinessHoursService:
    @staticmethod
    def get_hours(db: Session, business_id: UUID):
        business = get_business_or_404(db, business_id)

        return [
            format_hour_response(h)
            for h in (business.hours or [])
        ]

    @staticmethod
    def set_hours(
    db: Session,
    business_id: UUID,
    hours_data,
    user_id):
        business = get_business_or_404(db, business_id)

        # AUTH 
        check_business_owner(business, user_id)

        # delete old
        db.query(BusinessHours).filter(
            BusinessHours.business_id == business_id
        ).delete(synchronize_session=False)

        seen_days = set()
        new_hours_entries = []

        for item in hours_data:
            day_name = item.day_of_week.value if hasattr(item.day_of_week, 'value') else item.day_of_week

            # duplicate check
            if day_name in seen_days:
                raise HTTPException(400, f"Duplicate day: {day_name}")
            seen_days.add(day_name)

            # normalize
            try:
                open_t = normalize_time(item.open_time) if item.open_time else None
                close_t = normalize_time(item.close_time) if item.close_time else None
            except Exception:
                raise HTTPException(400, "Invalid time format.")

            # validate
            if item.is_open:
                validate_time_logic(open_t, close_t, day_name)

            new_hours_entries.append(
                BusinessHours(
                    business_id=business_id,
                    day_of_week=DAY_MAP.get(day_name),
                    is_open=item.is_open,
                    open_time=open_t,
                    close_time=close_t
                )
            )

        try:
            db.add_all(new_hours_entries)
            db.commit()
            return BusinessHoursService.get_hours(db, business_id)

        except Exception as e:
            db.rollback()
            raise HTTPException(500, "Database error")

    @staticmethod
    def update_hour(
        db: Session,
        business_id: UUID,
        hour_id: UUID,
        update_data,
        user_id
    ):
        business = get_business_or_404(db, business_id)

        # AUTH
        check_business_owner(business, user_id)

        # REAL UUID QUERY
        target_hour = (
            db.query(BusinessHours)
            .filter(
                BusinessHours.id == hour_id,
                BusinessHours.business_id == business_id
            )
            .first()
        )

        if not target_hour:
            raise HTTPException(404, "Hour entry not found")

        # update
        if update_data.is_open is not None:
            target_hour.is_open = update_data.is_open

        if update_data.open_time is not None:
            target_hour.open_time = normalize_time(update_data.open_time)

        if update_data.close_time is not None:
            target_hour.close_time = normalize_time(update_data.close_time)

        # validate
        if target_hour.is_open:
            validate_time_logic(
                target_hour.open_time,
                target_hour.close_time
            )

        # save
        commit_and_refresh(db, target_hour)

        return format_hour_response(target_hour)
