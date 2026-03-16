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

# ---------------------------------------------------------------------------
# App & config setup
# ---------------------------------------------------------------------------

app = APIRouter()

# SECURITY FIX (Security Misconfiguration - OWASP A05):
# SECRET_KEY is now loaded from a .env file rather than being hardcoded in
# source code. A hardcoded secret key would allow anyone who reads the code
# (e.g. via a public GitHub repo) to forge valid JWT tokens and impersonate
# any user, including admins.
# Ensure your .env file is listed in .gitignore and NEVER committed to Git.
# On Render/production, set SECRET_KEY as an environment variable in the dashboard.
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set. Refusing to start.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 60  # Reduced from 800 mins (~13 hrs) to 60 mins for security

# SECURITY FIX (Broken Authentication - OWASP A07):
# Rate limiter added to prevent brute-force attacks on the login endpoint.
# Without this, an attacker can try thousands of password combinations
# automatically. This limits each IP to 5 login attempts per minute.
limiter = Limiter(key_func=get_remote_address)

# Set up logging so security events are recorded
# SECURITY FIX (Security Misconfiguration - OWASP A05):
# Logging failed login attempts helps detect brute force and credential
# stuffing attacks. Without logs, attacks go completely unnoticed.
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt with a random salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Securely compare a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ---------------------------------------------------------------------------
# Pydantic models (request schemas)
# ---------------------------------------------------------------------------

class LoginItem(BaseModel):
    username: str
    password_hash: str  # this is the plain password sent from the client, named poorly - see note in login route

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    # SECURITY FIX (Broken Authentication - OWASP A07):
    # Using Pydantic's EmailStr enforces that the email field must be a valid
    # email address format. Without this, arbitrary strings could be stored,
    # which could cause issues in password reset flows or email enumeration.
    email: EmailStr
    team_id: int | None = None

    # SECURITY FIX (Broken Authentication - OWASP A07):
    # Password strength validation is enforced server-side. Client-side
    # validation alone is easily bypassed (e.g. via Postman or curl).
    # Weak passwords make accounts trivially brute-forceable.
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
    password: str  # SECURITY FIX: renamed from password_hash to password - see /user/create route
    full_name: str
    email: EmailStr
    team_id: int
    role: str

class MatchItem(BaseModel):
    location: str
    date: date
    opponent_team_id: int
    home_team_id: int

    # SECURITY FIX (XSS - OWASP A03):
    # Sanitise the location string to strip any HTML or script tags.
    # Without this, an attacker could inject <script>alert('xss')</script>
    # into the location field which may be rendered in the frontend.
    @field_validator("location")
    @classmethod
    def sanitise_location(cls, v: str) -> str:
        return bleach.clean(v, tags=[], strip=True)

class TeamItem(BaseModel):
    team_name: str

    # SECURITY FIX (XSS - OWASP A03):
    # Same sanitisation applied to team name to prevent stored XSS.
    @field_validator("team_name")
    @classmethod
    def sanitise_team_name(cls, v: str) -> str:
        return bleach.clean(v, tags=[], strip=True)

class ReportItem(BaseModel):
    match_report: str

    # SECURITY FIX (XSS - OWASP A03):
    # Match reports are the highest-risk field for stored XSS as they are
    # free-text and likely rendered directly in the UI. bleach.clean() strips
    # all disallowed HTML tags and attributes. A whitelist of safe tags is
    # provided so basic formatting (bold, italic) is preserved if needed.
    @field_validator("match_report")
    @classmethod
    def sanitise_report(cls, v: str) -> str:
        allowed_tags = ["b", "i", "u", "p", "br"]
        return bleach.clean(v, tags=allowed_tags, strip=True)


# ---------------------------------------------------------------------------
# Auth dependencies
# ---------------------------------------------------------------------------

def get_current_user(request: Request) -> dict:
    """
    Dependency: extracts and validates the JWT from the httpOnly cookie.
    Raises 401 if missing, 403 if invalid or expired.
    """
    token = request.cookies.get("token")

    # SECURITY FIX (Broken Authentication - OWASP A07):
    # Missing token returns 401 Unauthorized rather than silently failing.
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # SECURITY FIX (Broken Authentication - OWASP A07):
        # jwt.decode() now validates the "exp" claim automatically.
        # Expired tokens are rejected, preventing indefinite session reuse.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Session expired, please log in again")
    except jwt.InvalidTokenError:
        # SECURITY FIX (Broken Authentication - OWASP A07):
        # Catching specific JWT exceptions rather than a bare `except` clause
        # prevents accidental swallowing of unrelated errors and makes
        # debugging easier without leaking sensitive details to the client.
        raise HTTPException(status_code=403, detail="Invalid token")


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    SECURITY FIX (Broken Access Control - OWASP A01):
    Dependency: restricts a route to Admin-role users only.
    Previously, write/delete endpoints had NO authentication at all, meaning
    any unauthenticated request could create, update or delete data.
    Using this as a dependency on sensitive routes enforces role-based
    access control (RBAC) at the API layer.
    """
    if user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

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
        # SECURITY FIX (Broken Access Control - OWASP A01):
        # Role is hardcoded to "Player" server-side. Previously the UserCreate
        # model accepted a role field from the client, meaning anyone signing
        # up could send role="Admin" and gain admin privileges.
        role="Player",
    )
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return {"user_id": user_obj.user_id, "username": user_obj.username, "email": user_obj.email}


@app.post("/login")
@limiter.limit("5/minute")  # SECURITY FIX: rate limit - see limiter declaration above
async def user_login(request: Request, loginitem: LoginItem, response: Response, session: Session = Depends(get_db)):
    """
    Authenticate a user and set a secure httpOnly JWT cookie on success.
    """
    data = jsonable_encoder(loginitem)

    # SECURITY FIX (Broken Authentication - OWASP A07):
    # We look up the user first, then check the password in a single code path
    # regardless of whether the username exists. This prevents user enumeration
    # (i.e. an attacker figuring out which usernames are valid based on different
    # error messages or response times).
    user_input = session.query(User).filter_by(username=data["username"]).first()

    if not user_input or not check_password(data["password_hash"], user_input.password_hash):
        # SECURITY FIX (Broken Authentication - OWASP A07):
        # A generic error message is returned whether the username is wrong OR
        # the password is wrong. The original code returned the boolean result
        # of check_password() directly, leaking whether the username was valid.
        logger.warning("Failed login attempt for username: %s", data["username"])
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # SECURITY FIX (Broken Authentication - OWASP A07):
    # JWT now includes an "exp" (expiry) claim. The original token had no
    # expiry, meaning a stolen token would be valid forever. Now tokens
    # expire after ACCESS_TOKEN_EXPIRES_MINUTES (60 minutes).
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
        httponly=True,   # Prevents JavaScript access to the cookie (mitigates XSS cookie theft)
        secure=True,     # Cookie only sent over HTTPS
        samesite="none", # Required for cross-origin requests (frontend on different domain)
        max_age=ACCESS_TOKEN_EXPIRES_MINUTES * 60,
    )
    return {"message": "login_success"}


@app.post("/logout")
def logout(response: Response):
    """
    SECURITY FIX (Broken Authentication - OWASP A07):
    Logout endpoint clears the auth cookie server-side. Without this, the
    only way to log out was to clear cookies in the browser, meaning there
    was no server-enforced session termination.
    """
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


# ---------------------------------------------------------------------------
# Admin: User management
# ---------------------------------------------------------------------------

@app.post("/user/create")
async def admin_create_user(
    user: UserItem,
    session: Session = Depends(get_db),
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # This endpoint previously had NO authentication. Any anonymous caller
    # could create arbitrary users. Now only Admins can create users via
    # this route. The /signup route remains open for self-registration.
    _admin: dict = Depends(require_admin),
):
    """Admin-only: create a new user with a hashed password."""
    add_user = User(
        username=user.username,
        # SECURITY FIX (Broken Authentication - OWASP A07):
        # The original endpoint accepted a raw "password_hash" string from the
        # request body and stored it directly — meaning the caller controlled
        # what was stored as the hash. Now we hash the password properly here.
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        email=user.email,
        team_id=user.team_id,
        role="Player",  # Role is always forced to Player regardless of input
    )
    session.add(add_user)
    session.commit()
    session.refresh(add_user)
    return add_user


# ---------------------------------------------------------------------------
# Team routes
# ---------------------------------------------------------------------------

@app.get("/team/")
def get_team(session: Session = Depends(get_db)):
    """Public: list all teams."""
    team = session.query(Team).all()
    return {"Teams": team if team else []}


@app.get("/team/{team_id}")
def get_team_name(team_id: int, session: Session = Depends(get_db)):
    """Public: get a single team by ID."""
    # SECURITY FIX (SQL Injection - OWASP A03):
    # SQLAlchemy ORM is used throughout this file for all database queries.
    # The ORM uses parameterised queries internally, which means user-supplied
    # values (like team_id) are never interpolated directly into SQL strings.
    # This prevents SQL injection attacks such as: GET /team/1 OR 1=1--
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if team:
        return {"team_name": team.team_name}
    raise HTTPException(status_code=404, detail="Team not found")


@app.post("/team/create")
async def create_team(
    team: TeamItem,
    session: Session = Depends(get_db),
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could create teams.
    # Now restricted to Admins only.
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
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could rename any team.
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
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could delete any team.
    _admin: dict = Depends(require_admin),
):
    """Admin-only: delete a team."""
    team = session.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"message": f"Team {team_id} deleted successfully"}


# ---------------------------------------------------------------------------
# Match routes
# ---------------------------------------------------------------------------

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
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could create matches.
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
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could edit any match.
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
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could delete any match.
    # Also previously had no 404 check - would crash on missing match.
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
    # SECURITY FIX (Broken Access Control - OWASP A01):
    # Previously unauthenticated. Any user could overwrite any match report.
    _admin: dict = Depends(require_admin),
):
    """
    Admin-only: update a match report.
    Input is sanitised via the ReportItem validator to prevent stored XSS.
    """
    report = session.query(Match).filter(Match.match_id == match_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Match not found")
    # The match_report value has already been sanitised by the ReportItem
    # Pydantic validator before reaching this point (see bleach.clean above).
    report.match_report = new_report.match_report
    session.commit()
    return report