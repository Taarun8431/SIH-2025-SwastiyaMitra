from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/encounter", tags=["encounters"])

@router.post("/add", response_model=schemas.Encounter)
async def add_encounter(
    encounter: schemas.EncounterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_doctor_or_admin)
):
    """Add a new encounter (requires doctor or admin role)"""
    # Verify migrant exists
    db_migrant = crud.get_migrant(db, migrant_id=encounter.migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    # Create encounter with doctor ID
    return crud.create_encounter(db=db, encounter=encounter, doctor_id=current_user.id)

@router.get("/{encounter_id}", response_model=schemas.Encounter)
async def get_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get encounter details"""
    db_encounter = crud.get_encounter(db, encounter_id=encounter_id)
    if db_encounter is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    return db_encounter

@router.get("/", response_model=List[schemas.Encounter])
async def list_encounters(
    skip: int = 0,
    limit: int = 100,
    migrant_id: Optional[int] = Query(None, description="Filter by migrant ID"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """List encounters with optional migrant filtering"""
    encounters = crud.get_encounters(db, skip=skip, limit=limit, migrant_id=migrant_id)
    return encounters

@router.put("/{encounter_id}", response_model=schemas.Encounter)
async def update_encounter(
    encounter_id: int,
    encounter_update: schemas.EncounterUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_doctor_or_admin)
):
    """Update encounter (requires doctor or admin role)"""
    db_encounter = crud.get_encounter(db, encounter_id=encounter_id)
    if db_encounter is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    # Check if current user is the doctor who created the encounter or is admin
    if current_user.role != "admin" and db_encounter.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own encounters"
        )
    
    return crud.update_encounter(db=db, encounter_id=encounter_id, encounter_update=encounter_update)

@router.delete("/{encounter_id}")
async def delete_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Delete encounter (admin only)"""
    if crud.delete_encounter(db=db, encounter_id=encounter_id):
        return {"message": "Encounter deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Encounter not found")

@router.get("/migrant/{migrant_id}", response_model=List[schemas.Encounter])
async def get_migrant_encounters(
    migrant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all encounters for a specific migrant"""
    # Verify migrant exists
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    # Check consent
    consents = crud.get_consents_by_migrant(db, migrant_id=migrant_id)
    has_consent = len(consents) > 0
    
    if not has_consent and current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="No consent given to view encounters"
        )
    
    encounters = crud.get_encounters(db, skip=skip, limit=limit, migrant_id=migrant_id)
    
    # Log consent check if viewing encounters
    if has_consent and encounters:
        consent_log = schemas.ConsentLogCreate(
            migrant_id=migrant_id,
            action="viewed_encounters",
            consented=True
        )
        crud.create_consent_log(db=db, consent_log=consent_log, actor_id=current_user.id)
    
    return encounters
