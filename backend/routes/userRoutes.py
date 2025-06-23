from fastapi import APIRouter, Request, Response, Depends, HTTPException
import jwt
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.models import User
from backend.schemas.schemas import LoginItem, UserCreate, UserItem
from backend.auth.auth import ALGORITHM, SECRET_KEY, get_password_hash, check_password, create_jwt_token, ACCESS_TOKEN_EXPIRES_MINUTES
from fastapi.encoders import jsonable_encoder

app = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    new_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        email=user.email,
        team_id=user.team_id,
        role="Player"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(loginitem: LoginItem, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == loginitem.username).first()
    if user and check_password(loginitem.password_hash, user.password_hash):
        token = create_jwt_token(user)
        response.set_cookie(key="token", value=token, httponly=True, max_age=ACCESS_TOKEN_EXPIRES_MINUTES * 60)
        return {"message": "login_success"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

def get_current_user(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/me")
def read_me(user: dict = Depends(get_current_user)):
    return {
        "username": user["username"],
        "role": user["role"],
        "team_id": user["team_id"],
        "full_name": user["full_name"]
    }

@app.post("/user/create")
async def create_user(user: UserItem,db: Session = Depends(get_db)):
    add_user = User(
    username = user.username,
    password_hash = user.password_hash,
    full_name = user.full_name,
    email = user.email,
    team_id = user.team_id,
    role = "Player"
    
    )
    db.add(add_user)
    db.commit()
    db.refresh(add_user)
    return add_user 