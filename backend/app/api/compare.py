from fastapi import APIRouter, Query
from sqlalchemy import text
from backend.app.db.connection import engine

router = APIRouter()

@router.get("/compare")
def compare_properties(property_ids: list[int] = Query(...)):
    try:
        # Convert list to string for SQL query
        ids_str = ",".join(map(str, property_ids))

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT id, title, city, price, type, size
                FROM properties
                WHERE id IN ({ids_str})
            """))

            properties = [dict(row._mapping) for row in result]

        if not properties:
            return {"message": "No properties found"}

        #  ADD COMPARISON LOGIC
        for p in properties:
            p["price_per_sqft"] = round(p["price"] / p["size"], 2)

        best_price = min(properties, key=lambda x: x["price"])
        largest = max(properties, key=lambda x: x["size"])
        best_value = min(properties, key=lambda x: x["price_per_sqft"])

        return {
            "comparison": properties,
            "best_price": best_price,
            "largest_property": largest,
            "best_value_for_money": best_value
        }

    except Exception as e:
        return {"error": str(e)}
