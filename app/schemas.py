from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    username: str
    role: str = "worker"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Migrant schemas
class MigrantBase(BaseModel):
    name: str
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    district: Optional[str] = None
    district_in_kerala: Optional[str] = None
    occupation: Optional[str] = None
    abha_id: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class MigrantCreate(MigrantBase):
    pass

class MigrantUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    district: Optional[str] = None
    district_in_kerala: Optional[str] = None
    occupation: Optional[str] = None
    abha_id: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class Migrant(MigrantBase):
    id: int
    qr_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class MigrantWithEncounters(Migrant):
    encounters: List["Encounter"] = []
    consents: List["Consent"] = []

# Encounter schemas
class EncounterBase(BaseModel):
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    encounter_type: Optional[str] = None
    occurred_at: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class EncounterCreate(EncounterBase):
    migrant_id: int

class EncounterUpdate(BaseModel):
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    encounter_type: Optional[str] = None
    occurred_at: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class Encounter(EncounterBase):
    id: int
    migrant_id: int
    doctor_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Consent schemas
class ConsentBase(BaseModel):
    consent_text: str

class ConsentCreate(ConsentBase):
    migrant_id: int

class Consent(ConsentBase):
    id: int
    migrant_id: int
    given_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Consent Log schemas
class ConsentLogBase(BaseModel):
    action: str
    consented: bool

class ConsentLogCreate(ConsentLogBase):
    migrant_id: int

class ConsentLog(ConsentLogBase):
    id: int
    migrant_id: int
    actor_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Integration schemas
class ABHACreateRequest(BaseModel):
    name: str
    dob: str
    gender: str
    mobile: str

class ABHACreateResponse(BaseModel):
    abha_id: str
    status: str
    message: str

class AadhaarVerifyRequest(BaseModel):
    aadhaar_number: str
    otp: Optional[str] = None

class AadhaarVerifyResponse(BaseModel):
    verified: bool
    message: str

# Analytics schemas
class HeatmapRequest(BaseModel):
    level: str = Field(default="district", description="district or cluster")
    district: Optional[str] = None

class HeatmapResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[dict]

# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    message: str
    file_path: str
