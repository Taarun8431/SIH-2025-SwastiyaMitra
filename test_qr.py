#!/usr/bin/env python3
"""
Simple test script to verify QR code generation works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.utils.qr_utils import generate_basic_qr_code
    print("✅ QR utils import successful")
    
    # Test basic QR code generation
    test_data = "Test QR Code Data"
    qr_result = generate_basic_qr_code(test_data)
    print(f"✅ QR code generated successfully: {len(qr_result)} characters")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ QR generation error: {e}")

# Test database imports
try:
    from app import models, schemas, crud
    print("✅ Database imports successful")
except ImportError as e:
    print(f"❌ Database import error: {e}")

# Test route imports
try:
    from app.routes import migrant_routes
    print("✅ Route imports successful")
except ImportError as e:
    print(f"❌ Route import error: {e}")

print("Test completed.")
