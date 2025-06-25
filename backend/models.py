from sqlalchemy import Column, Integer, String, Date
from backend.database import Base

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
