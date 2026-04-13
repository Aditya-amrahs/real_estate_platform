from fastapi import APIRouter, Depends
from backend.app.db.connection import engine
from sqlalchemy import text
from backend.app.api.auth import require_agent
from backend.app.services.vector_search import add_property_embedding

router = APIRouter()

# ------------------ GET PROPERTIES ------------------

@router.get("/properties")
def get_properties(
    city: str = None,
    max_price: float = None,
    property_type: str = None,
    min_size: int = None
):
    try:
        query = "SELECT * FROM properties WHERE 1=1"
        params = {}

        if city:
            query += " AND city = :city"
            params["city"] = city

        if max_price:
            query += " AND price <= :price"
            params["price"] = max_price

        if property_type:
            query += " AND type = :type"
            params["type"] = property_type

        if min_size:
            query += " AND size >= :size"
            params["size"] = min_size

        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()

        return {"properties": [dict(r._mapping) for r in rows]}

    except Exception as e:
        return {"error": str(e)}


# ------------------ ADD PROPERTY ------------------

@router.post("/add-property")
def add_property(user=Depends(require_agent)):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT TOP 1 id FROM agents"))
            agent = result.fetchone()

            if not agent:
                return {"error": "No agent found"}

            agent_id = agent[0]

            conn.execute(text("""
                INSERT INTO properties (title, city, price, type, size, agent_id)
                VALUES ('2BHK Flat', 'Dehradun', 3000000, 'Apartment', 1200, :agent_id)
            """), {"agent_id": agent_id})

            result = conn.execute(text("""
                SELECT TOP 1 id FROM properties ORDER BY id DESC
            """))
            property_id = result.fetchone()[0]

        # vector embedding
        add_property_embedding(
            property_id,
            "2BHK Flat Dehradun Apartment"
        )

        return {"message": "Property added successfully"}

    except Exception as e:
        return {"error": str(e)}


# ------------------ GET SINGLE PROPERTY ------------------

@router.get("/properties/{property_id}")
def get_property(property_id: int):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM properties WHERE id = :id
            """), {"id": property_id})

            row = result.fetchone()

        if not row:
            return {"error": "Property not found"}

        return {"property": dict(row._mapping)}

    except Exception as e:
        return {"error": str(e)}


# ------------------ UPDATE PROPERTY ------------------

@router.put("/properties/{property_id}")
def update_property(property_id: int, title: str = None, price: float = None, user=Depends(require_agent)):
    try:
        query = "UPDATE properties SET "
        updates = []
        params = {"id": property_id}

        if title:
            updates.append("title = :title")
            params["title"] = title

        if price:
            updates.append("price = :price")
            params["price"] = price

        if not updates:
            return {"error": "No fields to update"}

        query += ", ".join(updates) + " WHERE id = :id"

        with engine.begin() as conn:
            conn.execute(text(query), params)

        return {"message": "Property updated successfully"}

    except Exception as e:
        return {"error": str(e)}


# ------------------ DELETE PROPERTY ------------------

@router.delete("/properties/{property_id}")
def delete_property(property_id: int, user=Depends(require_agent)):
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM properties WHERE id = :id
            """), {"id": property_id})

        return {"message": "Property deleted successfully"}

    except Exception as e:
        return {"error": str(e)}