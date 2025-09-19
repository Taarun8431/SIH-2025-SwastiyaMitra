from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import random
import string
import os
from datetime import datetime

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/integration", tags=["integration"])

@router.post("/abha/create", response_model=schemas.ABHACreateResponse)
async def create_abha_id(
    request: schemas.ABHACreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create ABHA ID (mock implementation)"""
    # Mock ABHA ID generation
    abha_id = f"ABHA-{''.join(random.choices(string.digits, k=14))}"
    
    return schemas.ABHACreateResponse(
        abha_id=abha_id,
        status="success",
        message="ABHA ID created successfully"
    )

@router.post("/aadhaar/verify", response_model=schemas.AadhaarVerifyResponse)
async def verify_aadhaar(
    request: schemas.AadhaarVerifyRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Verify Aadhaar number (mock implementation)"""
    # Mock verification - randomly return success/failure
    verified = random.choice([True, False])
    
    if verified:
        message = "Aadhaar verification successful"
    else:
        message = "Aadhaar verification failed"
    
    return schemas.AadhaarVerifyResponse(
        verified=verified,
        message=message
    )

@router.post("/upload-report", response_model=schemas.FileUploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    migrant_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Upload medical report file"""
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return schemas.FileUploadResponse(
            filename=filename,
            message="File uploaded successfully",
            file_path=file_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.post("/notify/sms")
async def send_sms_notification(
    phone: str,
    message: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Send SMS notification (mock implementation)"""
    # Mock SMS sending
    return {
        "status": "success",
        "message": f"SMS sent to {phone}",
        "content": message
    }

@router.post("/notify/email")
async def send_email_notification(
    email: str,
    subject: str,
    message: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Send email notification (mock implementation)"""
    # Mock email sending
    return {
        "status": "success",
        "message": f"Email sent to {email}",
        "subject": subject,
        "content": message
    }

@router.get("/health")
async def integration_health_check():
    """Health check for integration services"""
    return {
        "status": "healthy",
        "services": {
            "abha": "operational",
            "aadhaar": "operational",
            "file_upload": "operational",
            "notifications": "operational"
        },
        "timestamp": datetime.now().isoformat()
    }
