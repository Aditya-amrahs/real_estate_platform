from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from backend.app.db.connection import engine
from sqlalchemy import text
import os

SECRET_KEY = os.getenv("JWT_SECRET")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload["user_id"]

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, role FROM users WHERE id = :id"),
                {"id": user_id}
            )
            user = result.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {"id": user[0], "role": user[1]}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")