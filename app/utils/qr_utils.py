import qrcode
from io import BytesIO
import base64
from datetime import datetime

def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    today = datetime.now()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def generate_basic_qr_code(data: str) -> str:
    """
    Generate a simple QR code and return it as a base64 encoded string
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data and make the QR code
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_migrant_qr_code(migrant) -> str:
    """
    Generate QR code with basic patient details
    """
    # Calculate age from DOB if available
    age = "N/A"
    if migrant.dob:
        today = datetime.now()
        age = today.year - migrant.dob.year - ((today.month, today.day) < (migrant.dob.month, migrant.dob.day))
    
    # Create simple patient info string
    patient_info = f"""Patient ID: {migrant.id}
Name: {migrant.name or 'N/A'}
Age: {age}
Gender: {migrant.gender or 'N/A'}
Contact: {migrant.contact or 'N/A'}
District: {migrant.district_in_kerala or migrant.district or 'N/A'}
Registration: {migrant.created_at.strftime('%Y-%m-%d') if migrant.created_at else 'N/A'}"""
    
    return generate_basic_qr_code(patient_info)
