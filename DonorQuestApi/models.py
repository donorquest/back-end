import uuid, enum
from sqlalchemy import Column, String, DateTime, Enum, Boolean, Integer, ForeignKey, Date, JSON, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

def uuid4_str():
    import uuid as _u
    return str(_u.uuid4())

class Role(str, enum.Enum):
    DONOR = "DONOR"
    PATIENT = "PATIENT"
    ADMIN = "ADMIN"
    USER = "USER"

class RequestStatus(str, enum.Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"

class MatchStatus(str, enum.Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    RESPONDED_YES = "RESPONDED_YES"
    RESPONDED_NO = "RESPONDED_NO"
    EXPIRED = "EXPIRED"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uuid4_str)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.PATIENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    referal_code = Column(String, unique=True, nullable=True)

class Donor(Base):
    __tablename__ = "donors"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    full_name = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    city = Column(String); state = Column(String); pincode = Column(String)
    latitude = Column(Numeric(9,6)); longitude = Column(Numeric(9,6))
    available = Column(Boolean, default=True)
    last_donation_date = Column(Date, nullable=True)
    donations_count = Column(Integer, default=0)
    medical_flags = Column(JSON, default={})
    fcm_token = Column(String, nullable=True)

class PatientRequest(Base):
    __tablename__ = "patient_requests"
    id = Column(String, primary_key=True, default=uuid4_str)
    requester_user_id = Column(String, ForeignKey("users.id"))
    patient_name = Column(String, nullable=False)
    required_blood_group = Column(String, nullable=False)
    units = Column(Integer, nullable=False, default=1)
    hospital_name = Column(String, nullable=False)
    city = Column(String)
    latitude = Column(Numeric(9,6)); longitude = Column(Numeric(9,6))
    needed_by = Column(Date, nullable=True)
    notes = Column(String)
    phone = Column(Text, nullable=True)  # Added phone field
    registerd_user = Column(Boolean, default=True)  # Added registerd_user field
    status = Column(Enum(RequestStatus), default=RequestStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"
    id = Column(String, primary_key=True, default=uuid4_str)
    request_id = Column(String, ForeignKey("patient_requests.id"))
    donor_user_id = Column(String, ForeignKey("users.id"))
    match_score = Column(Numeric(5,2))
    status = Column(Enum(MatchStatus), default=MatchStatus.SENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    token = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    expires_at = Column(DateTime(timezone=True))

class Batch(Base):
    __tablename__ = "batches"
    id = Column(String, primary_key=True, default=uuid4_str)
    name = Column(String, nullable=False)
    city = Column(String)
    scheduled_on = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

class BatchDonor(Base):
    __tablename__ = "batch_donors"
    batch_id = Column(String, ForeignKey("batches.id"), primary_key=True)
    donor_user_id = Column(String, ForeignKey("users.id"), primary_key=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, nullable=True)
    method = Column(String); path = Column(String)
    status_code = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
