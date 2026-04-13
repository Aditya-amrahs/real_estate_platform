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

#  define class
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
#-------------REGISTER------------------
@router.post("/register")
def register(user: UserRegister):
    try:
        print("STEP 1")

        # temporarily avoid bcrypt issues
        hashed_password = user.password

        print("STEP 2")

        with engine.begin() as conn:
            print("STEP 3")

            conn.execute(text("""
                INSERT INTO users (name, email, password, role)
                VALUES (:name, :email, :password, :role)
            """), {
                "name": user.name,
                "email": user.email,
                "password": hashed_password,
                "role": "user"
            })

        print("STEP 4 SUCCESS")

        return {"message": "User registered successfully"}

    except Exception as e:
        print(" REGISTER ERROR:", e)
        return {"error": str(e)}



# ------------------ LOGIN  ------------------

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
                SELECT id, password FROM users WHERE email = :email
            """), {"email": user.email})

            db_user = result.fetchone()

        if not db_user:
            return {"error": "User not found"}

        user_id, hashed_password = db_user

        # ✅ HANDLE BOTH HASHED + PLAIN PASSWORD
        try:
            if hashed_password.startswith("$2b$"):
                valid = pwd_context.verify(user.password, hashed_password)
            else:
                valid = (user.password == hashed_password)
        except:
            valid = False

        if not valid:
            return {"error": "Invalid password"}

        token_data = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }

        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "message": "Login successful",
            "token": token
        }

    except Exception as e:
        return {"error": str(e)}
    
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

        return payload["user_id"]

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")