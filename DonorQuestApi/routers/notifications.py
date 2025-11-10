from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Match
from auth import admin_required
from services.fcm import send_to_token
from sqlalchemy import text

router = APIRouter()

@router.post("/user/{user_id}")
def push_user(user_id: str, title: str, body: str, db: Session = Depends(get_db), _=Depends(admin_required)):
    row = db.execute(text("SELECT donors.fcm_token FROM donors WHERE donors.user_id = :uid"), {"uid": user_id}).fetchone()
    if not row or not row.fcm_token:
        raise HTTPException(400, "No FCM token for user")
    send_to_token(row.fcm_token, title, body, {"user_id": user_id})
    return {"ok": True}

@router.post("/match/{match_id}")
def push_match(match_id: str, title: str = "Blood needed", body: str = "Please respond", db: Session = Depends(get_db), _=Depends(admin_required)):
    m = db.get(Match, match_id)
    if not m: raise HTTPException(404, "Match not found")
    row = db.execute(text("SELECT fcm_token FROM donors WHERE user_id=:uid"), {"uid": m.donor_user_id}).fetchone()
    if not row or not row.fcm_token: raise HTTPException(400, "No FCM token")
    deep_link = f"app://match/{match_id}"
    send_to_token(row.fcm_token, title, body, {"match_id": match_id, "deeplink": deep_link})
    return {"ok": True, "deeplink": deep_link}
