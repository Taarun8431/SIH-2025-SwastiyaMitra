from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import crud, models, schemas, auth
from ..database import get_db
from ..utils.qr_utils import generate_migrant_qr_code

router = APIRouter(prefix="/migrant", tags=["migrants"])

@router.post("/register", response_model=schemas.Migrant)
async def register_migrant(
    migrant: schemas.MigrantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Register a new migrant and generate QR code"""
    # Create migrant
    db_migrant = crud.create_migrant(db=db, migrant=migrant)
    
    # Generate simple QR code with basic patient details
    qr_code = generate_migrant_qr_code(db_migrant)
    crud.update_migrant_qr_code(db=db, migrant_id=db_migrant.id, qr_code=qr_code)
    
    # Refresh to get updated QR code
    db.refresh(db_migrant)
    return db_migrant

@router.get("/{migrant_id}", response_model=schemas.MigrantWithEncounters)
async def get_migrant(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get migrant details with encounters (check consent if enabled)"""
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    # Check if user has consent to view detailed information
    consents = crud.get_consents_by_migrant(db, migrant_id=migrant_id)
    has_consent = len(consents) > 0
    
    # Log consent check
    if has_consent:
        consent_log = schemas.ConsentLogCreate(
            migrant_id=migrant_id,
            action="viewed",
            consented=True
        )
        crud.create_consent_log(db=db, consent_log=consent_log, actor_id=current_user.id)
    
    return db_migrant

@router.get("/", response_model=List[schemas.Migrant])
async def list_migrants(
    skip: int = 0,
    limit: int = 100,
    district: Optional[str] = Query(None, description="Filter by district"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """List migrants with optional district filtering"""
    migrants = crud.get_migrants(db, skip=skip, limit=limit, district=district)
    return migrants

@router.put("/{migrant_id}", response_model=schemas.Migrant)
async def update_migrant(
    migrant_id: int,
    migrant_update: schemas.MigrantUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update migrant information"""
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    return crud.update_migrant(db=db, migrant_id=migrant_id, migrant_update=migrant_update)

@router.delete("/{migrant_id}")
async def delete_migrant(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Delete migrant (admin only)"""
    if crud.delete_migrant(db=db, migrant_id=migrant_id):
        return {"message": "Migrant deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Migrant not found")

@router.get("/{migrant_id}/qr")
async def get_migrant_qr_code(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get migrant's QR code"""
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    if not db_migrant.qr_code:
        # Generate QR code if it doesn't exist
        qr_code = generate_migrant_qr_code(db_migrant)
        crud.update_migrant_qr_code(db=db, migrant_id=migrant_id, qr_code=qr_code)
        db.refresh(db_migrant)
    
    return {"qr_code": db_migrant.qr_code}

@router.get("/{migrant_id}/complete")
async def get_migrant_complete_data(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get complete migrant data including all medical records for QR scanning"""
    migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if not migrant:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    # Get all encounters for this migrant
    encounters = crud.get_migrant_encounters(db, migrant_id=migrant_id)
    
    # Format encounters data
    encounters_data = []
    for encounter in encounters:
        encounters_data.append({
            "id": encounter.id,
            "symptoms": encounter.symptoms,
            "diagnosis": encounter.diagnosis,
            "treatment": encounter.treatment,
            "encounter_type": encounter.encounter_type,
            "notes": encounter.notes,
            "occurred_at": encounter.occurred_at,
            "created_at": encounter.created_at,
            "doctor": encounter.doctor.username if encounter.doctor else None
        })
    
    # Return complete migrant data
    return {
        "migrant": {
            "id": migrant.id,
            "name": migrant.name,
            "dob": migrant.dob,
            "age": migrant.age,
            "gender": migrant.gender,
            "contact": migrant.contact,
            "phone": migrant.phone,
            "language": migrant.language,
            "district": migrant.district,
            "district_in_kerala": migrant.district_in_kerala,
            "occupation": migrant.occupation,
            "abha_id": migrant.abha_id,
            "location_lat": migrant.location_lat,
            "location_lng": migrant.location_lng,
            "created_at": migrant.created_at,
            "qr_code": migrant.qr_code
        },
        "encounters": encounters_data,
        "total_encounters": len(encounters_data),
        "last_visit": encounters_data[0]["occurred_at"] if encounters_data else None
    }

@router.post("/{migrant_id}/regenerate-qr")
async def regenerate_qr_code(
    migrant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Regenerate QR code for migrant"""
    db_migrant = crud.get_migrant(db, migrant_id=migrant_id)
    if db_migrant is None:
        raise HTTPException(status_code=404, detail="Migrant not found")
    
    # Generate new QR code
    qr_code = generate_migrant_qr_code(db_migrant)
    crud.update_migrant_qr_code(db=db, migrant_id=migrant_id, qr_code=qr_code)
    
    return {"message": "QR code regenerated successfully", "qr_code": qr_code}
