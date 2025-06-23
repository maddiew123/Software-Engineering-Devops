import bcrypt
import jwt
from fastapi import HTTPException
from datetime import timedelta
from backend.database import SessionLocal
from backend.models.models import User

SECRET_KEY = "SECRET_TEE_HEE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 800

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_jwt_token(user):
    payload = {
        "username": user.username,
        "team_id": user.team_id,
        "role": user.role,
        "full_name": user.full_name
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
