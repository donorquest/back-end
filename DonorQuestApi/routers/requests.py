from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models import User, PatientRequest, Donor, Match, MatchStatus, Role,RequestStatus
from schemas import RequestIn
from auth import current_user
from matching import compatible_groups, cooldown_ok

router = APIRouter()

@router.post("/blood-request")
def create_request(payload: RequestIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    print("/blood-request payload:", payload.model_dump())
    req = PatientRequest(requester_user_id=user.id, **payload.model_dump())
    db.add(req); db.commit(); db.refresh(req)
    return {"id": req.id}

@router.post("/blood-request/public")
def create_public_request(payload: RequestIn, db: Session = Depends(get_db)):
    req = PatientRequest(requester_user_id=None, **payload.model_dump())
    db.add(req); db.commit(); db.refresh(req)
    return {"id": req.id}

@router.get("/{rid}")
def get_request(rid: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    req = db.get(PatientRequest, rid)
    if not req: raise HTTPException(404, "Request not found")
    return {"id": req.id, "status": req.status.value, "required_blood_group": req.required_blood_group, "created_at": str(req.created_at)}

@router.post("/{rid}/match")
def run_match(rid: str, radius_km: float = 15.0, top_n: int = 30, db: Session = Depends(get_db), user: User = Depends(current_user)):
    req = db.get(PatientRequest, rid)
    if not req: raise HTTPException(404, "Request not found")
    comp = compatible_groups(req.required_blood_group)
    if not comp: raise HTTPException(400, "Invalid blood group")
    # PostGIS query: donors within radius + cooldown 90d + available
    sql = text("""
        SELECT d.user_id, d.full_name, d.blood_group, d.latitude, d.longitude,
               ST_Distance(ST_MakePoint(:rlon, :rlat)::geography, ST_MakePoint(d.longitude, d.latitude)::geography) / 1000.0 AS km
        FROM donors d
        WHERE d.available = TRUE
          AND d.blood_group = ANY(:comp)
          AND (d.last_donation_date IS NULL OR d.last_donation_date <= CURRENT_DATE - INTERVAL '90 days')
          AND ST_DWithin(ST_MakePoint(:rlon, :rlat)::geography, ST_MakePoint(d.longitude, d.latitude)::geography, :meters)
        ORDER BY km ASC
        LIMIT :top_n
    """)
    rows = db.execute(sql, {
        "rlat": float(req.latitude),
        "rlon": float(req.longitude),
        "meters": radius_km * 1000.0,
        "comp": list(comp),
        "top_n": int(top_n)
    }).fetchall()
    out = []
    for r in rows:
        m = Match(request_id=req.id, donor_user_id=r.user_id, match_score=max(0.0, 100.0 - float(r.km)))
        db.add(m); db.flush()
        out.append({"match_id": m.id, "donor_user_id": r.user_id, "distance_km": round(float(r.km),2)})
    db.commit()
    return {"request_id": req.id, "matches": out}

@router.get("/blood-request/open")
def get_open_requests(db: Session = Depends(get_db), user: User = Depends(current_user)):
    print("/blood-request/open:")
    open_requests = db.query(PatientRequest).filter(PatientRequest.status == RequestStatus.OPEN).all()
    return [
        {
            "id": req.id,
            "patient_name": req.patient_name,
            "hospital_name": req.hospital_name,
            "city": req.city,
            "required_blood_group": req.required_blood_group,
            "created_at": str(req.created_at),
            "status": req.status.value
        }
        for req in open_requests
    ]
