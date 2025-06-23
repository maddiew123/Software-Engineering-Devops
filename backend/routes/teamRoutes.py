from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.models import Team
from backend.schemas.schemas import TeamItem

app = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/team/{team_id}")
def get_team_name(team_id: int,db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if team:
        return {"team_name": team.team_name}
    else:
        return {"team_name": "Unknown Team"}
    

@app.get("/team/")
def get_team(db: Session = Depends(get_db)):
    team = db.query(Team).all()
    if team:
        return {"Teams": team}
    else:
        return {"Teams": "Unknown Team"}

@app.post("/team/create")
async def create_team(team: TeamItem,db: Session = Depends(get_db)):
    add_team = Team(
        team_name=team.team_name
    
    )
    db.add(add_team)
    db.commit()
    db.refresh(add_team)
    return add_team

@app.put("/team/update/{team_id}")
def update_team(team_id: int, new_team: TeamItem,db: Session = Depends(get_db)):

    team = db.query(Team).filter(Team.team_id == team_id).first()
    
    team.team_name=new_team.team_name
    
    
    db.commit()

    return team

@app.delete("/team/delete/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):

    team = db.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()

    return team