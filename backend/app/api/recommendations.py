from fastapi import APIRouter
from sqlalchemy import text
from backend.app.db.connection import engine
from backend.app.services.vector_search import get_similar_ids

router = APIRouter()

@router.get("/recommend")
def recommend(query: str):

    ids = get_similar_ids(query)

    if not ids:
        return {"status": "success", "data": []}

    placeholders = ",".join([f":id{i}" for i in range(len(ids))])
    params = {f"id{i}": ids[i] for i in range(len(ids))}

    query_sql = text(f"""
        SELECT * FROM properties
        WHERE id IN ({placeholders})
    """)

    with engine.connect() as conn:
        result = conn.execute(query_sql, params)

        return {"status": "success", "data": [dict(r._mapping) for r in result]}