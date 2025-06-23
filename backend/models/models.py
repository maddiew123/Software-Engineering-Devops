from pydantic import BaseModel
from datetime import date
from sqlalchemy import Column, Integer, String, Date
from backend.database import Base

class Team(Base):
    __tablename__ = "team"
    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String)

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True)
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

# class LoginItem(BaseModel):
#     username: str
#     password_hash: str

# class UserCreate(BaseModel):
#     username: str
#     password: str
#     full_name: str
#     email: str
#     team_id: int | None = None
#     role: str | None = "user"

# class UserItem(BaseModel):
#     username: str
#     password_hash: str
#     full_name: str
#     email: str
#     team_id: int
#     role: str

# class MatchItem(BaseModel):
#     location: str
#     date: date
#     opponent_team_id: int
#     home_team_id: int

# class TeamItem(BaseModel):
#     team_name: str

# class ReportItem(BaseModel):
#     match_report: str