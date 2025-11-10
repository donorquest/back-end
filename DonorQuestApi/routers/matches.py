from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Match, MatchStatus, User
from auth import current_user
from datetime import datetime

router = APIRouter()

@router.get("")
def my_matches(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Match).filter(Match.donor_user_id==user.id).order_by(Match.created_at.desc()).limit(100).all()
    return [ {"id": m.id, "status": m.status.value, "created_at": str(m.created_at), "score": float(m.match_score or 0)} for m in rows ]

@router.post("/{mid}/respond")
def respond(mid: str, response: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    m = db.get(Match, mid)
    if not m: raise HTTPException(404, "Match not found")
    if m.donor_user_id != user.id: raise HTTPException(403, "Not your match")
    if response.lower() == "yes": m.status = MatchStatus.RESPONDED_YES
    else: m.status = MatchStatus.RESPONDED_NO
    m.responded_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "status": m.status.value}
