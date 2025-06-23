from pydantic import BaseModel
from datetime import date

class LoginItem(BaseModel):
    username: str
    password_hash: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    team_id: int | None = None
    role: str | None = "Player"

class UserItem(BaseModel):
    username: str
    password_hash: str
    full_name: str
    email: str
    team_id: int
    role: str

class MatchItem(BaseModel):
    location: str
    date: date
    opponent_team_id: int
    home_team_id: int

class TeamItem(BaseModel):
    team_name: str

class ReportItem(BaseModel):
    match_report: str
