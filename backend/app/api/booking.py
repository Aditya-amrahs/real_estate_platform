from fastapi import APIRouter
from backend.app.db.connection import engine
from sqlalchemy import text

router = APIRouter()

# ------------------ BOOK VISIT ------------------

@router.post("/book-visit")
def book_visit(user_id: int, property_id: int, visit_date: str, visit_time: str):
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

        return {"message": "Booking successful"}

    except Exception as e:
        return {"error": str(e)}