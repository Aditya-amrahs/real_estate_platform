from fastapi import APIRouter
from sqlalchemy import text
from backend.app.db.connection import engine

router = APIRouter()

@router.get("/dashboard/{agent_id}")
def dashboard(agent_id: int):

    with engine.connect() as conn:

        total_properties = conn.execute(text("""
            SELECT COUNT(*) FROM properties WHERE agent_id = :id
        """), {"id": agent_id}).scalar()

        total_bookings = conn.execute(text("""
            SELECT COUNT(*) FROM bookings
            WHERE property_id IN (
                SELECT id FROM properties WHERE agent_id = :id
            )
        """), {"id": agent_id}).scalar()

    return {
        "total_properties": total_properties,
        "total_bookings": total_bookings
    }