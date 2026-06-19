from fastapi import HTTPException


def commit_and_refresh(db, obj):
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except Exception as e:
        db.rollback()
        raise HTTPException(500, "Database error")