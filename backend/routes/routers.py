import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
import jwt
from pydantic import BaseModel
from sqlalchemy import or_
from backend.database.database import get_db

from backend.models import Match, Team, User
from sqlalchemy.orm import Session
from datetime import date
app = APIRouter()


SECRET_KEY = "SECRET_TEE_HEE"
ALGORITHM = "HS256"
ACCES_TOKEN_EXPRIES_MINUTES = 800

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
async def create_user(user: UserCreate, session: Session = Depends(get_db)):
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
async def user_login(loginitem: LoginItem, response: Response, session: Session = Depends(get_db)):
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
            samesite="none",
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
async def create_user(user: UserItem, session: Session = Depends(get_db)):
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
def get_team_name(team_id: int, session: Session = Depends(get_db)):
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if team:
        return {"team_name": team.team_name}
    else:
        return {"team_name": "Unknown Team"}
    

@app.get("/team/")
def get_team(session: Session = Depends(get_db)):
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
async def create_team(team: TeamItem, session: Session = Depends(get_db)):
    add_team = Team(
        team_name=team.team_name
    
    )
    session.add(add_team)
    session.commit()
    session.refresh(add_team)
    return add_team

@app.put("/team/update/{team_id}")
def update_team(team_id: int, new_team: TeamItem, session: Session = Depends(get_db)):

    team = session.query(Team).filter(Team.team_id == team_id).first()
    
    team.team_name=new_team.team_name
    
    
    session.commit()

    return team

@app.delete("/team/delete/{team_id}")
def delete_team(team_id: int, session: Session = Depends(get_db)):

    team = session.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()

    return team

@app.get("/match/")
def get_match(session: Session = Depends(get_db)):
    match = session.query(Match).all()
    if match:
        return {"Match": match}
    else:
        return {"Match": "Unknown Match"}

@app.post("/match/create")
async def create_match(match: MatchItem, session: Session = Depends(get_db)):
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
def update_match(match_id: int, new_match: MatchItem, session: Session = Depends(get_db)):

    match = session.query(Match).filter(Match.match_id == match_id).first()
    
    match.location=new_match.location
    match.date=new_match.date
    match.opponent_team_id=new_match.opponent_team_id
    match.home_team_id=new_match.home_team_id
    
    
    session.commit()

    return match

@app.delete("/match/delete/{match_id}")
def delete_match(match_id: int, session: Session = Depends(get_db)):

    match = session.query(Match).filter(Match.match_id == match_id).first()
    
    session.delete(match)
    session.commit()

    return match


@app.get("/match/team/{team_id}")
def get_user_match_by_team(team_id: int, session: Session = Depends(get_db)):
    match = session.query(Match).filter(or_(Match.home_team_id == team_id , Match.opponent_team_id == team_id)).all()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"user_matches": match}
    
@app.get("/match/{match_id}")
def get_user_match(match_id: int, session: Session = Depends(get_db)):
    match = session.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"match": match}

class ReportItem(BaseModel):
    match_report: str

@app.put("/match/report/update/{match_id}")
def update_report(match_id: int, new_report: ReportItem, session: Session = Depends(get_db)):

    report = session.query(Match).filter(Match.match_id == match_id).first()
    
    report.match_report=new_report.match_report

    session.commit()

    return report

