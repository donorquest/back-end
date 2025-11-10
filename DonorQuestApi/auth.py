from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models import User, Role, RefreshToken
import uuid
from passlib.context import CryptContext
import bcrypt
print(bcrypt.__version__)

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],   # keep bcrypt so old hashes still verify
    deprecated="bcrypt"                    # new hashes use bcrypt_sha256
)
security = HTTPBearer()

def hash_password(p: str) -> str:
    # no truncation needed
    print(f"Hashed password: {p}")
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_access_token(sub: str, role: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.API_JWT_EXPIRES_MIN)
    return jwt.encode({"sub": sub, "role": role, "exp": expire}, settings.API_JWT_SECRET, algorithm="HS256")

def create_refresh_token(db: Session, user_id: str):
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(minutes=settings.API_REFRESH_EXPIRES_MIN)
    db.add(RefreshToken(token=token, user_id=user_id, expires_at=expires)); db.commit()
    return token

def current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.API_JWT_SECRET, algorithms=["HS256"])
        uid = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, uid)
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_required(user: User = Depends(current_user)):
    if user.role != Role.ADMIN: raise HTTPException(status_code=403, detail="Admin only")
    return user

def donor_required(user: User = Depends(current_user)):
    if user.role not in [Role.DONOR, Role.USER, Role.PATIENT]:
        raise HTTPException(status_code=403, detail="Donor access only")
    return user
