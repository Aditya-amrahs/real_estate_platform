from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from backend.app.db.connection import engine
from backend.app.api.auth import get_current_user

router = APIRouter()

@router.post("/book-visit")
def book_visit(property_id: int, visit_date: str, visit_time: str,
               user_id: int = Depends(get_current_user)):

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                EXEC book_visit :user_id, :property_id, :visit_date, :visit_time
            """), {
                "user_id": user_id,
                "property_id": property_id,
                "visit_date": visit_date,
                "visit_time": visit_time
            })

        return {"message": "Booking confirmed"}

    except Exception as e:
        if "Slot already booked" in str(e):
            raise HTTPException(400, "Slot already booked")
        raise HTTPException(500, str(e))