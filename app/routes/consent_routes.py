from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/consent", tags=["consent"])

@router.post("/", response_model=schemas.Consent)
async def create_consent(
    consent: schemas.ConsentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new consent record"""
    # Verify migrant exists
    db_migrant = crud.get_migrant(db, migrant_id=consent.migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    # Create consent
    db_consent = crud.create_consent(db=db, consent=consent)
    
    # Log consent action
    consent_log = schemas.ConsentLogCreate(
        migrant_id=consent.migrant_id,
        action="granted",
        consented=True
    )
    crud.create_consent_log(db=db, consent_log=consent_log, actor_id=current_user.id)
    
    return db_consent

@router.get("/migrant/{migrant_id}", response_model=List[schemas.Consent])
async def get_migrant_consents(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all active consents for a migrant"""
    # Verify migrant exists
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    consents = crud.get_consents_by_migrant(db, migrant_id=migrant_id)
    return consents

@router.put("/{consent_id}/revoke")
async def revoke_consent(
    consent_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Revoke a consent"""
    db_consent = crud.get_consent(db, consent_id=consent_id)
    if db_consent is None:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    # Revoke consent
    revoked_consent = crud.revoke_consent(db=db, consent_id=consent_id)
    
    # Log consent revocation
    consent_log = schemas.ConsentLogCreate(
        migrant_id=db_consent.migrant_id,
        action="revoked",
        consented=False
    )
    crud.create_consent_log(db=db, consent_log=consent_log, actor_id=current_user.id)
    
    return {"message": "Consent revoked successfully"}

@router.get("/logs", response_model=List[schemas.ConsentLog])
async def get_consent_logs(
    migrant_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_doctor_or_admin)
):
    """Get consent logs (requires doctor or admin role)"""
    logs = crud.get_consent_logs(db, migrant_id=migrant_id, skip=skip, limit=limit)
    return logs

@router.get("/check/{migrant_id}")
async def check_consent_status(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Check if migrant has given consent"""
    # Verify migrant exists
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    consents = crud.get_consents_by_migrant(db, migrant_id=migrant_id)
    has_consent = len(consents) > 0
    
    return {
        "migrant_id": migrant_id,
        "has_consent": has_consent,
        "active_consents": len(consents)
    }
