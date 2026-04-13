from fastapi import APIRouter, Header, HTTPException, Depends
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
    try:
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

    except Exception as e:
        return {"error": str(e)}


# ------------------ LOGIN ------------------

class UserLogin(BaseModel):
    email: str
    password: str

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

@router.post("/login")
def login(user: UserLogin):
    try:
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

    except Exception as e:
        return {"error": str(e)}


# ------------------ JWT AUTH ------------------

def get_current_user(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token missing")

        token = authorization.split(" ")[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------ RBAC ------------------

def require_agent(user=Depends(get_current_user)):
    if user["role"] != "agent":
        raise HTTPException(status_code=403, detail="Only agents allowed")
    
    return user


# ------------------ GET USERS ------------------

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


# ------------------ DELETE USER ------------------

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM favorites WHERE user_id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM bookings WHERE user_id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM agents WHERE user_id = :id"), {"id": user_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})

        return {"message": "User deleted successfully"}

    except Exception as e:
        return {"error": str(e)}