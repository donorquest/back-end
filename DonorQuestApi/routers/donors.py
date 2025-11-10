from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Donor, User, Role
from schemas import DonorIn
from auth import current_user, admin_required

router = APIRouter()

@router.post("/profile")
def upsert_donor(payload: DonorIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    print("/profile payload:", payload.model_dump())
    if user.role not in (Role.DONOR, Role.ADMIN):
        raise HTTPException(403, "Only donors/admin can update donor profile")
    donor = db.query(Donor).filter(Donor.user_id==user.id).first()
    if not donor:
        donor = Donor(user_id=user.id, **payload.model_dump())
        db.add(donor)
    else:
        for k,v in payload.model_dump().items(): setattr(donor, k, v)
    db.commit()
    return {"ok": True, "user_id": user.id}

@router.get("/me")
def get_me(db: Session = Depends(get_db), user: User = Depends(current_user)):
    d = db.query(Donor).filter(Donor.user_id==user.id).first()
    if not d: raise HTTPException(404, "Donor profile not found")
    return d.__dict__

@router.get("/search")
def search(blood_group: str = None, city: str = None, available: bool = None, db: Session = Depends(get_db), _=Depends(admin_required)):
    q = db.query(Donor)
    if blood_group: q = q.filter(Donor.blood_group==blood_group)
    if city: q = q.filter(Donor.city.ilike(f"%{city}%"))
    if available is not None: q = q.filter(Donor.available==available)
    return [{
        "user_id": d.user_id, "full_name": d.full_name, "bg": d.blood_group,
        "city": d.city, "available": d.available
    } for d in q.limit(100).all()]
