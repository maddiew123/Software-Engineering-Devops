from datetime import date, timedelta
import random
from unittest.mock import Base
import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import jwt
from pydantic import BaseModel
from sqlalchemy import Column, Date, Integer, String, create_engine, or_
from sqlalchemy.orm import declarative_base, sessionmaker
import os
Base = declarative_base()

class Team(Base):
    __tablename__ = "team"

    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_name = Column (String)

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String)
    password_hash = Column (String)
    full_name = Column(String)
    email = Column(String)
    team_id = Column(Integer)
    role = Column(String)

class Match(Base):
    __tablename__ = "match"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location = Column(String)
    date = Column(Date)
    opponent_team_id = Column(Integer)
    home_team_id = Column(Integer)
    match_report = Column(String)

engine = create_engine("sqlite:///database.db")


Session = sessionmaker(bind=engine)
session = Session()

DB_PATH = "database.db"

if not os.path.exists(DB_PATH):
    Base.metadata.create_all(engine)
    session = Session()

    for i in range(1,11):
        new_team = Team(team_id=i, team_name="Team " + str(i))
        session.add(new_team)

    for i in range(1, 11):
        names = [
        "Alice Johnson",
        "Benjamin Carter",
        "Clara Rodriguez",
        "David Thompson",
        "Ella Nguyen",
        "Franklin White",
        "Grace Patel",
        "Henry Kim",
        "Isla Martinez",
        "Jack Robinson"
    ]
    usernames = [
        "alice_johnson",
        "ben_carter23",
        "clara.rod",
        "david_t",
        "ella.nguyen",
        "frank_white91",
        "grace_patel7",
        "henrykim",
        "isla.m",
        "jackr_88"
    ]

    for i in range(0, 10):
        new_user = User(
            username= usernames[i],
            password_hash="$2b$12$yCP4nkODQUVznnmgKYKpAeGvFgi7jsgIn37dLXbBNwiEE4cVdyT6q",
            full_name=names[i],
            email=f"user{i}@example.com",
            team_id=random.randint(0, 10),
            role="Player"
        )
        session.add(new_user)
    new_user = User(
            username= "admin",
            password_hash="$2b$12$BSyRxFYhVVrjzAlQXUl1.eKi6A/91z4Y1IePaVIeB0KZTaUvJrjfO",
            full_name="admin",
            email=f"admin@example.com",
            team_id=random.randint(0, 10),
            role="Manager"
        )
    session.add(new_user)

    for i in range(1, 100):
        locations = ["London", "Paris", "Liverpool", "Cornwal", "Miami"]
        opponent_team_id=random.randint(1, 10)
        home_team_id=random.randint(1, 10)
        while opponent_team_id == home_team_id:
            home_team_id=random.randint(1, 10)

        match = Match(
                location=random.choice(locations),
                date=date.today() + timedelta(days=i),
                opponent_team_id=opponent_team_id,
                home_team_id=home_team_id,
                match_report=""   
            )
        session.add(match)

SECRET_KEY = "SECRET_TEE_HEE"
ALGORITHM = "HS256"
ACCES_TOKEN_EXPRIES_MINUTES = 800

app = FastAPI()

origins = ["https://software-engineering-agile-assignment-3.onrender.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')  

class LoginItem(BaseModel):
    username: str
    password_hash: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    team_id: int | None = None
    role: str | None = "user"

@app.post("/signup")
async def create_user(user: UserCreate):
    existing_user = session.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user_obj = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        email=user.email,
        team_id=user.team_id,
        role="Player",
    )
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return {"user_id": user_obj.user_id, "username": user_obj.username, "email": user_obj.email}

def check_password(plain_password: str, hashed_password: str) -> bool:

        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.post("/login")
async def user_login(loginitem: LoginItem, response: Response):
    data = jsonable_encoder(loginitem)
    user_input = session.query(User).filter_by(username=data['username']).first()
    if data['username']== user_input.username and check_password(data['password_hash'],user_input.password_hash):
        payload = {
            "username": user_input.username,
            "team_id": user_input.team_id,
            "role": user_input.role,
            "full_name": user_input.full_name
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=True,  
            samesite="Lax",
            max_age=ACCES_TOKEN_EXPRIES_MINUTES * 60
        )
        return {"message": "login_success"}
    else:
        return {"message": check_password(data['password_hash'],user_input.password_hash)}


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
    
class UserItem(BaseModel):
    username: str
    password_hash: str
    full_name: str
    email: str
    team_id: int
    role: str

@app.post("/user/create")
async def create_user(user: UserItem):
    add_user = User(
    username = user.username,
    password_hash = user.password_hash,
    full_name = user.full_name,
    email = user.email,
    team_id = user.team_id,
    role = "Player"
    
    )
    session.add(add_user)
    session.commit()
    session.refresh(add_user)
    return add_user   
    
@app.get("/team/{team_id}")
def get_team_name(team_id: int):
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if team:
        return {"team_name": team.team_name}
    else:
        return {"team_name": "Unknown Team"}
    

@app.get("/team/")
def get_team():
    team = session.query(Team).all()
    if team:
        return {"Teams": team}
    else:
        return {"Teams": "Unknown Team"}

class MatchItem(BaseModel):
    location: str
    date: date
    opponent_team_id: int
    home_team_id: int

class TeamItem(BaseModel):
    team_name: str

@app.post("/team/create")
async def create_team(team: TeamItem):
    add_team = Team(
        team_name=team.team_name
    
    )
    session.add(add_team)
    session.commit()
    session.refresh(add_team)
    return add_team

@app.put("/team/update/{team_id}")
def update_team(team_id: int, new_team: TeamItem):

    team = session.query(Team).filter(Team.team_id == team_id).first()
    
    team.team_name=new_team.team_name
    
    
    session.commit()

    return team

@app.delete("/team/delete/{team_id}")
def delete_team(team_id: int):

    team = session.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()

    return team

@app.get("/match/")
def get_match():
    match = session.query(Match).all()
    if match:
        return {"Match": match}
    else:
        return {"Match": "Unknown Match"}

@app.post("/match/create")
async def create_match(match: MatchItem):
    add_match = Match(
        location=match.location,
        date=match.date,
        opponent_team_id=match.opponent_team_id,
        home_team_id=match.home_team_id,
        match_report=""
    )
    session.add(add_match)
    session.commit()
    session.refresh(add_match)
    return add_match
    

@app.put("/match/update/{match_id}")
def update_match(match_id: int, new_match: MatchItem):

    match = session.query(Match).filter(Match.match_id == match_id).first()
    
    match.location=new_match.location
    match.date=new_match.date
    match.opponent_team_id=new_match.opponent_team_id
    match.home_team_id=new_match.home_team_id
    
    
    session.commit()

    return match

@app.delete("/match/delete/{match_id}")
def delete_match(match_id: int):

    match = session.query(Match).filter(Match.match_id == match_id).first()
    
    session.delete(match)
    session.commit()

    return match

@app.get("/")
def read_root():
    return session.query(User).all()



@app.get("/match/team/{team_id}")
def get_user_match(team_id: int):
    match = session.query(Match).filter(or_(Match.home_team_id == team_id , Match.opponent_team_id == team_id)).all()
    if match:
        return {"user_match": match}
    else:
        return {"user_match": "Unknown match"}
    
@app.get("/match/{match_id}")
def get_user_match(match_id: int):
    match = session.query(Match).filter(Match.match_id == match_id).first()
    if match:
        return {"user_match": match}
    else:
        return {"team_name": "Unknown match"}
    

class ReportItem(BaseModel):
    match_report: str

@app.put("/match/report/update/{match_id}")
def update_report(match_id: int, new_report: ReportItem):

    report = session.query(Match).filter(Match.match_id == match_id).first()
    
    report.match_report=new_report.match_report

    session.commit()

    return report

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
