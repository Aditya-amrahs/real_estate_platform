from fastapi import APIRouter, Depends
from backend.app.db.connection import engine
from backend.app.api.auth import get_current_user
from sqlalchemy import text

router = APIRouter()

# ------------------ ADD TO FAVORITES ------------------

@router.post("/favorites")
def add_favorite(property_id: int, user_id: int = Depends(get_current_user)):
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO favorites (user_id, property_id)
                VALUES (:user_id, :property_id)
            """), {
                "user_id": user_id,
                "property_id": property_id
            })

        return {"message": "Added to favorites"}

    except Exception as e:
        return {"error": str(e)}


# ------------------ GET FAVORITES ------------------

@router.get("/favorites")
def get_favorites(user_id: int = Depends(get_current_user)):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT p.*
                FROM favorites f
                JOIN properties p ON f.property_id = p.id
                WHERE f.user_id = :user_id
            """), {"user_id": user_id})

            rows = result.fetchall()

        return {"favorites": [dict(r._mapping) for r in rows]}

    except Exception as e:
        return {"error": str(e)}