from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models import PatientRequest, Donor, Batch, BatchDonor, User
from auth import admin_required
import pandas as pd
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter()

@router.get("/requests")
def list_requests(db: Session = Depends(get_db), _=Depends(admin_required)):
    rows = db.query(PatientRequest).order_by(PatientRequest.created_at.desc()).limit(500).all()
    return [r.__dict__ for r in rows]

@router.get("/donors")
def list_donors(
    city: str | None = None,
    blood_group: str | None = None,
    available: bool | None = None,
    db: Session = Depends(get_db),
    _=Depends(admin_required)
):
    q = db.query(Donor, User).join(User, Donor.user_id == User.id)
    if city:
        q = q.filter(Donor.city.ilike(f"%{city}%"))
    if blood_group:
        q = q.filter(Donor.blood_group == blood_group)
    if available is not None:
        q = q.filter(Donor.available == available)
    rows = q.limit(1000).all()
    return [
        {
            "user_id": d.user_id,
            "name": d.full_name,
            "bg": d.blood_group,
            "city": d.city,
            "phone": u.phone,  # phone from User table
            "available": d.available
        }
        for d, u in rows
    ]
@router.get("/reports/requests.csv")
def requests_csv(db: Session = Depends(get_db), _=Depends(admin_required)):
    df = pd.read_sql(text("SELECT id, required_blood_group, units, city, status, created_at FROM patient_requests ORDER BY created_at DESC"), db.bind)
    buf = StringIO(); df.to_csv(buf, index=False); buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=requests.csv"})

@router.post("/batches")
def create_batch(name: str, city: str = "", scheduled_on: str | None = None, db: Session = Depends(get_db), _=Depends(admin_required)):
    b = Batch(name=name, city=city, scheduled_on=scheduled_on if scheduled_on else None)
    db.add(b); db.commit(); db.refresh(b)
    return {"id": b.id, "name": b.name}

@router.post("/batches/{bid}/add")
def add_to_batch(bid: str, donor_user_id: str, db: Session = Depends(get_db), _=Depends(admin_required)):
    db.add(BatchDonor(batch_id=bid, donor_user_id=donor_user_id)); db.commit()
    return {"ok": True}

@router.get("/batches")
def list_batches(db: Session = Depends(get_db), _=Depends(admin_required)):
    rows = db.query(Batch).order_by(Batch.scheduled_on).all()
    return [ {"id": b.id, "name": b.name, "city": b.city, "scheduled_on": str(b.scheduled_on) if b.scheduled_on else None} for b in rows ]
