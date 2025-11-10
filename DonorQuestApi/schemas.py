from pydantic import BaseModel, EmailStr
from typing import Optional, List

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str = "PATIENT"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class DonorIn(BaseModel):
    full_name: str
    blood_group: str
    city: str
    state: str
    pincode: str
    latitude: float
    longitude: float
    available: bool = True
    last_donation_date: Optional[str] = None

class RequestIn(BaseModel):
    patient_name: str
    required_blood_group: str
    units: int = 1
    hospital_name: str
    city: str
    latitude: float
    longitude: float
    needed_by: Optional[str] = None
    notes: Optional[str] = None
    phone: Optional[str] = None
    registerd_user: Optional[bool] = True
