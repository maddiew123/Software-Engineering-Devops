from datetime import date, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

engine = create_engine("sqlite:///./database.db")

Session = sessionmaker(bind=engine)

def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()

