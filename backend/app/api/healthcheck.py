# app/api/healthcheck.py

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.deps import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
def health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database readiness check failed",
            )
        return {"status": "ok", "db_connection": "ok"}
    except HTTPException:
        raise
    except Exception:
        # Never return driver exceptions: they may contain host/user details.
        logger.error("Database readiness check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    
# @router.get("")
# def health_check():
#     return {"status": "ok"}
