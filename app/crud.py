from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import Optional, List
from . import models, schemas
from .auth import get_password_hash
import datetime

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Migrant CRUD operations
def get_migrant(db: Session, migrant_id: int):
    return db.query(models.Migrant).filter(models.Migrant.id == migrant_id).first()

def get_migrants(db: Session, skip: int = 0, limit: int = 100, district: Optional[str] = None):
    query = db.query(models.Migrant)
    if district:
        query = query.filter(or_(
            models.Migrant.district == district,
            models.Migrant.district_in_kerala == district
        ))
    return query.offset(skip).limit(limit).all()

def create_migrant(db: Session, migrant: schemas.MigrantCreate):
    db_migrant = models.Migrant(**migrant.dict())
    db.add(db_migrant)
    db.commit()
    db.refresh(db_migrant)
    return db_migrant

def update_migrant(db: Session, migrant_id: int, migrant_update: schemas.MigrantUpdate):
    db_migrant = db.query(models.Migrant).filter(models.Migrant.id == migrant_id).first()
    if db_migrant:
        update_data = migrant_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_migrant, field, value)
        
        db.commit()
        db.refresh(db_migrant)
    return db_migrant

def delete_migrant(db: Session, migrant_id: int):
    db_migrant = db.query(models.Migrant).filter(models.Migrant.id == migrant_id).first()
    if db_migrant:
        db.delete(db_migrant)
        db.commit()
        return True
    return False

def update_migrant_qr_code(db: Session, migrant_id: int, qr_code: str):
    db_migrant = db.query(models.Migrant).filter(models.Migrant.id == migrant_id).first()
    if db_migrant:
        db_migrant.qr_code = qr_code
        db.commit()
        db.refresh(db_migrant)
    return db_migrant

# Encounter CRUD operations
def get_encounter(db: Session, encounter_id: int):
    return db.query(models.Encounter).filter(models.Encounter.id == encounter_id).first()

def get_encounters(db: Session, skip: int = 0, limit: int = 100, migrant_id: Optional[int] = None):
    query = db.query(models.Encounter)
    if migrant_id:
        query = query.filter(models.Encounter.migrant_id == migrant_id)
    return query.offset(skip).limit(limit).all()


def get_migrant_encounters(db: Session, migrant_id: int):
    """Get all encounters for a specific migrant - used by QR scanner"""
    return db.query(models.Encounter).options(joinedload(models.Encounter.migrant)).filter(models.Encounter.migrant_id == migrant_id).all()


def create_encounter(db: Session, encounter: schemas.EncounterCreate, doctor_id: Optional[int] = None):
    encounter_data = encounter.dict()
    if doctor_id:
        encounter_data["doctor_id"] = doctor_id
    
    db_encounter = models.Encounter(**encounter_data)
    db.add(db_encounter)
    db.commit()
    db.refresh(db_encounter)
    return db_encounter

def update_encounter(db: Session, encounter_id: int, encounter_update: schemas.EncounterUpdate):
    db_encounter = db.query(models.Encounter).filter(models.Encounter.id == encounter_id).first()
    if db_encounter:
        update_data = encounter_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_encounter, field, value)
        
        db.commit()
        db.refresh(db_encounter)
    return db_encounter

def delete_encounter(db: Session, encounter_id: int):
    db_encounter = db.query(models.Encounter).filter(models.Encounter.id == encounter_id).first()
    if db_encounter:
        db.delete(db_encounter)
        db.commit()
        return True
    return False

# Consent CRUD operations
def get_consent(db: Session, consent_id: int):
    return db.query(models.Consent).filter(models.Consent.id == consent_id).first()

def get_consents_by_migrant(db: Session, migrant_id: int):
    return db.query(models.Consent).filter(
        and_(models.Consent.migrant_id == migrant_id, models.Consent.is_active == True)
    ).all()

def create_consent(db: Session, consent: schemas.ConsentCreate):
    db_consent = models.Consent(**consent.dict())
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def revoke_consent(db: Session, consent_id: int):
    db_consent = db.query(models.Consent).filter(models.Consent.id == consent_id).first()
    if db_consent:
        db_consent.is_active = False
        db.commit()
        db.refresh(db_consent)
    return db_consent

# Consent Log CRUD operations
def create_consent_log(db: Session, consent_log: schemas.ConsentLogCreate, actor_id: int):
    db_consent_log = models.ConsentLog(
        **consent_log.dict(),
        actor_id=actor_id
    )
    db.add(db_consent_log)
    db.commit()
    db.refresh(db_consent_log)
    return db_consent_log

def get_consent_logs(db: Session, migrant_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.ConsentLog)
    if migrant_id:
        query = query.filter(models.ConsentLog.migrant_id == migrant_id)
    return query.order_by(models.ConsentLog.timestamp.desc()).offset(skip).limit(limit).all()

# Analytics functions
def get_migrants_by_district(db: Session):
    """Get count of migrants grouped by district"""
    return db.query(
        models.Migrant.district_in_kerala,
        func.count(models.Migrant.id).label('count')
    ).group_by(models.Migrant.district_in_kerala).all()

def get_encounters_by_district(db: Session):
    """Get count of encounters grouped by district"""
    return db.query(
        models.Migrant.district_in_kerala,
        func.count(models.Encounter.id).label('count')
    ).join(models.Encounter).group_by(models.Migrant.district_in_kerala).all()

def get_migrants_near_location(db: Session, lat: float, lng: float, radius_km: float = 10):
    """Get migrants within radius of a location"""
    point = f"POINT({lng} {lat})"
    return db.query(models.Migrant).filter(
        func.ST_DWithin(models.Migrant.location, func.ST_GeogFromText(point), radius_km * 1000)
    ).all()
