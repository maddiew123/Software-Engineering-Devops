import os
from backend.database.database import engine, Base, Session
from backend.models import Team, User, Match
from datetime import date, timedelta
import random

DB_PATH = "database.db"

def create_database(): 

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
        session.commit()
        session.close()

