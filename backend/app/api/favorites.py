from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from backend.app.db.connection import engine
from backend.app.api.auth import get_current_user

router = APIRouter()

@router.post("/favorites")
def add_favorite(property_id: int, user_id: int = Depends(get_current_user)):
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO favorites (user_id, property_id)
                VALUES (:user_id, :property_id)
            """), {"user_id": user_id, "property_id": property_id})

        return {"status": "success", "message": "Added to favorites"}

    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(400, "Already in favorites")
        raise HTTPException(500, str(e))


@router.get("/favorites")
def get_favorites(user_id: int = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.*
            FROM favorites f
            JOIN properties p ON f.property_id = p.id
            WHERE f.user_id = :user_id
        """), {"user_id": user_id})

        return {"status": "success", "data": [dict(r._mapping) for r in result]}
    