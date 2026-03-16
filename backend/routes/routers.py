import bcrypt
import bleach
import os
import logging
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.database.database import get_db
from backend.models import Match, Team, User

app = APIRouter()

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set. Refusing to start.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 60  

limiter = Limiter(key_func=get_remote_address)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt with a random salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Securely compare a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


class LoginItem(BaseModel):
    username: str
    password_hash: str  

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: EmailStr
    team_id: int | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserItem(BaseModel):
    username: str
    password: str  
    full_name: str
    email: EmailStr
    team_id: int
    role: str

class MatchItem(BaseModel):
    location: str
    date: date
    opponent_team_id: int
    home_team_id: int

    @field_validator("location")
    @classmethod
    def sanitise_location(cls, v: str) -> str:
        return bleach.clean(v, tags=[], strip=True)

class TeamItem(BaseModel):
    team_name: str
    @field_validator("team_name")
    @classmethod
    def sanitise_team_name(cls, v: str) -> str:
        return bleach.clean(v, tags=[], strip=True)

class ReportItem(BaseModel):
    match_report: str
    @classmethod
    def sanitise_report(cls, v: str) -> str:
        allowed_tags = ["b", "i", "u", "p", "br"]
        return bleach.clean(v, tags=allowed_tags, strip=True)

def get_current_user(request: Request) -> dict:
    """
    Dependency: extracts and validates the JWT from the httpOnly cookie.
    Raises 401 if missing, 403 if invalid or expired.
    """
    token = request.cookies.get("token")

 
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Session expired, please log in again")
    except jwt.InvalidTokenError:

        raise HTTPException(status_code=403, detail="Invalid token")


def require_admin(user: dict = Depends(get_current_user)) -> dict:

    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.post("/signup")
async def create_user(user: UserCreate, session: Session = Depends(get_db)):
    """Register a new user. All new accounts are assigned the 'Player' role."""
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


@app.post("/login")
@limiter.limit("5/minute") 
async def user_login(request: Request, loginitem: LoginItem, response: Response, session: Session = Depends(get_db)):
    """
    Authenticate a user and set a secure httpOnly JWT cookie on success.
    """
    data = jsonable_encoder(loginitem)

    user_input = session.query(User).filter_by(username=data["username"]).first()

    if not user_input or not check_password(data["password_hash"], user_input.password_hash):
        logger.warning("Failed login attempt for username: %s", data["username"])
        raise HTTPException(status_code=401, detail="Invalid username or password")
    payload = {
        "username": user_input.username,
        "team_id": user_input.team_id,
        "role": user_input.role,
        "full_name": user_input.full_name,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,   
        secure=True,     
        samesite="none", 
        max_age=ACCESS_TOKEN_EXPIRES_MINUTES * 60,
    )
    return {"message": "login_success"}


@app.post("/logout")
def logout(response: Response):

    response.delete_cookie(key="token", httponly=True, secure=True, samesite="none")
    return {"message": "logged_out"}


@app.get("/me")
def read_me(user: dict = Depends(get_current_user)):
    """Return the current authenticated user's profile from their JWT."""
    return {
        "username": user["username"],
        "role": user["role"],
        "team_id": user["team_id"],
        "full_name": user["full_name"],
    }


@app.post("/user/create")
async def admin_create_user(
    user: UserItem,
    session: Session = Depends(get_db),
  
    _admin: dict = Depends(require_admin),
):
    """Admin-only: create a new user with a hashed password."""
    add_user = User(
        username=user.username,

        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        email=user.email,
        team_id=user.team_id,
        role="Player", 
    )
    session.add(add_user)
    session.commit()
    session.refresh(add_user)
    return add_user



@app.get("/team/")
def get_team(session: Session = Depends(get_db)):
    """Public: list all teams."""
    team = session.query(Team).all()
    return {"Teams": team if team else []}


@app.get("/team/{team_id}")
def get_team_name(team_id: int, session: Session = Depends(get_db)):
    """Public: get a single team by ID."""
   
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if team:
        return {"team_name": team.team_name}
    raise HTTPException(status_code=404, detail="Team not found")


@app.post("/team/create")
async def create_team(
    team: TeamItem,
    session: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Admin-only: create a new team."""
    add_team = Team(team_name=team.team_name)
    session.add(add_team)
    session.commit()
    session.refresh(add_team)
    return add_team


@app.put("/team/update/{team_id}")
def update_team(
    team_id: int,
    new_team: TeamItem,
    session: Session = Depends(get_db),
    
    _admin: dict = Depends(require_admin),
):
    """Admin-only: update a team's name."""
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.team_name = new_team.team_name
    session.commit()
    return team


@app.delete("/team/delete/{team_id}")
def delete_team(
    team_id: int,
    session: Session = Depends(get_db),

    _admin: dict = Depends(require_admin),
):
    """Admin-only: delete a team."""
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"message": f"Team {team_id} deleted successfully"}


@app.get("/match/")
def get_match(session: Session = Depends(get_db)):
    """Public: list all matches."""
    match = session.query(Match).all()
    return {"Match": match if match else []}


@app.get("/match/team/{team_id}")
def get_user_match_by_team(team_id: int, session: Session = Depends(get_db)):
    """Public: get all matches involving a specific team."""
    match = session.query(Match).filter(
        or_(Match.home_team_id == team_id, Match.opponent_team_id == team_id)
    ).all()
    if not match:
        raise HTTPException(status_code=404, detail="No matches found for this team")
    return {"user_matches": match}


@app.get("/match/{match_id}")
def get_user_match(match_id: int, session: Session = Depends(get_db)):
    """Public: get a single match by ID."""
    match = session.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"match": match}


@app.post("/match/create")
async def create_match(
    match: MatchItem,
    session: Session = Depends(get_db),
   
    _admin: dict = Depends(require_admin),
):
    """Admin-only: create a new match."""
    add_match = Match(
        location=match.location,
        date=match.date,
        opponent_team_id=match.opponent_team_id,
        home_team_id=match.home_team_id,
        match_report="",
    )
    session.add(add_match)
    session.commit()
    session.refresh(add_match)
    return add_match


@app.put("/match/update/{match_id}")
def update_match(
    match_id: int,
    new_match: MatchItem,
    session: Session = Depends(get_db),

    _admin: dict = Depends(require_admin),
):
    """Admin-only: update match details."""
    match = session.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.location = new_match.location
    match.date = new_match.date
    match.opponent_team_id = new_match.opponent_team_id
    match.home_team_id = new_match.home_team_id
    session.commit()
    return match


@app.delete("/match/delete/{match_id}")
def delete_match(
    match_id: int,
    session: Session = Depends(get_db),
  
    _admin: dict = Depends(require_admin),
):
    """Admin-only: delete a match."""
    match = session.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    session.delete(match)
    session.commit()
    return {"message": f"Match {match_id} deleted successfully"}


@app.put("/match/report/update/{match_id}")
def update_report(
    match_id: int,
    new_report: ReportItem,
    session: Session = Depends(get_db),
   
    _admin: dict = Depends(require_admin),
):
    """
    Admin-only: update a match report.
    Input is sanitised via the ReportItem validator to prevent stored XSS.
    """
    report = session.query(Match).filter(Match.match_id == match_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Match not found")
    report.match_report = new_report.match_report
    session.commit()
    return report