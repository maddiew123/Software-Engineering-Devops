
from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.models import Match
from backend.schemas.schemas import MatchItem, ReportItem

app = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/match/")
def get_match(db: Session = Depends(get_db)):
    match = db.query(Match).all()
    if match:
        return {"Match": match}
    else:
        return {"Match": "Unknown Match"}

@app.post("/match/create")
async def create_match(match: MatchItem,db: Session = Depends(get_db)):
    add_match = Match(
        location=match.location,
        date=match.date,
        opponent_team_id=match.opponent_team_id,
        home_team_id=match.home_team_id,
        match_report=""
    )
    db.add(add_match)
    db.commit()
    db.refresh(add_match)
    return add_match
    

@app.put("/match/update/{match_id}")
def update_match(match_id: int, new_match: MatchItem,db: Session = Depends(get_db)):

    match = db.query(Match).filter(Match.match_id == match_id).first()
    
    match.location=new_match.location
    match.date=new_match.date
    match.opponent_team_id=new_match.opponent_team_id
    match.home_team_id=new_match.home_team_id
    
    
    db.commit()

    return match

@app.delete("/match/delete/{match_id}")
def delete_match(match_id: int,db: Session = Depends(get_db)):

    match = db.query(Match).filter(Match.match_id == match_id).first()
    
    db.delete(match)
    db.commit()

    return match

@app.get("/match/team/{team_id}")
def get_user_match(team_id: int,db: Session = Depends(get_db)):
    match = db.query(Match).filter(or_(Match.home_team_id == team_id , Match.opponent_team_id == team_id)).all()
    if match:
        return {"user_match": match}
    else:
        return {"user_match": "Unknown match"}
    
@app.get("/match/{match_id}")
def get_user_match(match_id: int,db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if match:
        return {"user_match": match}
    else:
        return {"team_name": "Unknown match"}

@app.put("/match/report/update/{match_id}")
def update_report(match_id: int, new_report: ReportItem,db: Session = Depends(get_db)):

    report = db.query(Match).filter(Match.match_id == match_id).first()
    
    report.match_report=new_report.match_report

    db.commit()

    return report