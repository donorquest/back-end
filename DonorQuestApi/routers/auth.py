from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role, RefreshToken, Donor
from schemas import UserCreate, LoginIn, TokenOut
from auth import hash_password, verify_password, create_access_token, current_user, create_refresh_token
import logging
import uuid

router = APIRouter()
logger = logging.getLogger("auth")

@router.post("/register", response_model=TokenOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Register attempt for email: {payload.email}")
    logger.info(f"Register attempt for Password: {payload.password}")
    if db.query(User).filter(User.email==payload.email).first():
        logger.warning(f"Registration failed: Email already registered: {payload.email}")
        raise HTTPException(400, "Email already registered")
    # Generate unique referal code starting with DQ
    referal_code = "DQ" + uuid.uuid4().hex[:4].upper()
    while db.query(User).filter(User.referal_code==referal_code).first():
        referal_code = "DQ" + uuid.uuid4().hex[:4].upper()
    # Truncate password to 72 bytes before hashing
    user = User(email=payload.email, phone=payload.phone, password_hash=hash_password(payload.password), role=Role(payload.role), referal_code=referal_code)
    db.add(user); db.commit(); db.refresh(user)
    logger.info(f"User registered: {user.email} (id={user.id}) referal_code={user.referal_code}")
    at = create_access_token(user.id, user.role.value)
    rt = create_refresh_token(db, user.id)
    return {"access_token": at, "refresh_token": rt}

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {payload.email}")
    user = db.query(User).filter(User.email==payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(f"Login failed for email: {payload.email}")
        raise HTTPException(401, "Invalid credentials")
    logger.info(f"Login successful for email: {user.email} (id={user.id})")
    at = create_access_token(user.id, user.role.value)
    rt = create_refresh_token(db, user.id)
    return {"access_token": at, "refresh_token": rt}

@router.post("/refresh", response_model=TokenOut)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    row = db.query(RefreshToken).filter(RefreshToken.token==refresh_token).first()
    if not row: raise HTTPException(401, "Invalid refresh token")
    from datetime import datetime
    if row.expires_at < datetime.utcnow(): raise HTTPException(401, "Refresh token expired")
    user = db.get(User, row.user_id)
    at = create_access_token(user.id, user.role.value)
    rt = create_refresh_token(db, user.id)
    return {"access_token": at, "refresh_token": rt}

@router.get("/me")
def me(user=Depends(current_user), db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.user_id==user.id).first()
    return {"id": user.id, "email": user.email, "role": user.role.value, "has_donor_profile": bool(donor)}

@router.post("/me/fcm")
def save_fcm(token: str, user=Depends(current_user), db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.user_id==user.id).first()
    if donor:
        donor.fcm_token = token; db.commit()
        return {"ok": True}
    return {"ok": False, "reason": "not a donor"}
