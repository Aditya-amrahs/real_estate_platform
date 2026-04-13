# imports
from fastapi import APIRouter
from backend.app.db.connection import engine
from sqlalchemy import text
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------ REGISTER ------------------

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str   # user or agent

@router.post("/register")
def register(user: UserRegister):
    hashed_password = pwd_context.hash(user.password)

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (name, email, password, role)
            VALUES (:name, :email, :password, :role)
        """), {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "role": user.role
        })

    return {"message": "User registered successfully"}


# ------------------ LOGIN  ------------------

class UserLogin(BaseModel):
    email: str
    password: str

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

@router.post("/login")
def login(user: UserLogin):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, password, role FROM users WHERE email = :email
        """), {"email": user.email})

        db_user = result.fetchone()

    if not db_user:
        return {"error": "User not found"}

    user_id, hashed_password, role = db_user

    if not pwd_context.verify(user.password, hashed_password):
        return {"error": "Invalid password"}

    # ✅ include role in token
    token_data = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message": "Login successful",
        "token": token
    }
#JWT AUTHENTICATION--------------------------
from fastapi import Header, HTTPException
from jose import jwt
import os

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token missing")

        token = authorization.split(" ")[1]  # Bearer <token>

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload   # returns user_id + role

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
from fastapi import HTTPException, Depends

def require_agent(user=Depends(get_current_user)):
    if user["role"] != "agent":
        raise HTTPException(status_code=403, detail="Only agents allowed")
    
    return user
#------------------ GET USERS (FOR TESTING) ------------------
@router.get("/users")
def get_users():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, name, email, role FROM users
            """))
            rows = result.fetchall()

        return {"users": [dict(r._mapping) for r in rows]}

    except Exception as e:
        return {"error": str(e)}
    from fastapi import Depends

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        with engine.begin() as conn:
            
            # delete favorites
            conn.execute(text("""
                DELETE FROM favorites WHERE user_id = :id
            """), {"id": user_id})

            # delete bookings
            conn.execute(text("""
                DELETE FROM bookings WHERE user_id = :id
            """), {"id": user_id})

            # delete agents linked to user
            conn.execute(text("""
                DELETE FROM agents WHERE user_id = :id
            """), {"id": user_id})

            # finally delete user
            conn.execute(text("""
                DELETE FROM users WHERE id = :id
            """), {"id": user_id})

        return {"message": "User deleted successfully"}

    except Exception as e:
        return {"error": str(e)}