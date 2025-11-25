#!/usr/bin/env python3
"""
Comprehensive API testing script for SIH Backend
Tests all endpoints and validates responses
"""

import requests
import json
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
    
    def test_health_check(self):
        """Test basic health endpoints"""
        self.log("Testing health check endpoints...")
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.base_url}/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            self.log("[OK] Root endpoint working")
        except Exception as e:
            self.log(f"[FAIL] Root endpoint failed: {e}", "ERROR")
            return False
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            self.log("[OK] Health endpoint working")
        except Exception as e:
            self.log(f"[FAIL] Health endpoint failed: {e}", "ERROR")
            return False
        
        return True
    
    def test_authentication(self):
        """Test authentication endpoints"""
        self.log("Testing authentication...")
        
        # Test login with default admin user
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = requests.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            
            # Store token for future requests
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.log("[OK] Login successful")
        except Exception as e:
            error_details = ""
            if 'response' in locals():
                error_details = f" Status: {response.status_code}, Response: {response.text}"
            self.log(f"[FAIL] Login failed: {e}{error_details}", "ERROR")
            return False
        
        # Test /auth/me endpoint
        try:
            response = requests.get(f"{self.base_url}/auth/me", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "admin"
            assert data["role"] == "admin"
            self.log("[OK] /auth/me working")
        except Exception as e:
            self.log(f"[FAIL] /auth/me failed: {e}", "ERROR")
            return False
        
        return True
    
    def test_migrant_operations(self):
        """Test migrant CRUD operations"""
        self.log("Testing migrant operations...")
        
        # Test migrant registration
        try:
            migrant_data = {
                "name": "Test Migrant",
                "gender": "Male",
                "contact": "+91-9999999999",
                "district_in_kerala": "Ernakulam",
                "occupation": "Test Worker",
                "location_lat": 9.9312,
                "location_lng": 76.2673
            }
            response = requests.post(
                f"{self.base_url}/migrant/register",
                json=migrant_data,
                headers=self.headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["name"] == "Test Migrant"
            assert "qr_code" in data
            
            migrant_id = data["id"]
            self.log(f"[OK] Migrant registered with ID: {migrant_id}")
        except Exception as e:
            error_details = ""
            if 'response' in locals():
                error_details = f" Status: {response.status_code}, Response: {response.text}"
            self.log(f"[FAIL] Migrant registration failed: {e}{error_details}", "ERROR")
            return False
        
        # Test get migrant
        try:
            response = requests.get(f"{self.base_url}/migrant/{migrant_id}", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == migrant_id
            assert data["name"] == "Test Migrant"
            self.log("[OK] Get migrant working")
        except Exception as e:
            self.log(f"[FAIL] Get migrant failed: {e}", "ERROR")
            return False
        
        # Test list migrants
        try:
            response = requests.get(f"{self.base_url}/migrant/", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            self.log("[OK] List migrants working")
        except Exception as e:
            self.log(f"[FAIL] List migrants failed: {e}", "ERROR")
            return False
        
        # Test QR code endpoint
        try:
            response = requests.get(f"{self.base_url}/migrant/{migrant_id}/qr", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert "qr_code" in data
            self.log("[OK] QR code endpoint working")
        except Exception as e:
            self.log(f"[FAIL] QR code endpoint failed: {e}", "ERROR")
            return False
        
        return migrant_id
    
    def test_encounter_operations(self, migrant_id):
        """Test encounter CRUD operations"""
        self.log("Testing encounter operations...")
        
        # Test add encounter
        try:
            encounter_data = {
                "migrant_id": migrant_id,
                "symptoms": "Test symptoms",
                "diagnosis": "Test diagnosis",
                "treatment": "Test treatment",
                "encounter_type": "consultation"
            }
            response = requests.post(
                f"{self.base_url}/encounter/add",
                json=encounter_data,
                headers=self.headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["migrant_id"] == migrant_id
            
            encounter_id = data["id"]
            self.log(f"[OK] Encounter added with ID: {encounter_id}")
        except Exception as e:
            self.log(f"[FAIL] Add encounter failed: {e}", "ERROR")
            return False
        
        # Test get encounter
        try:
            response = requests.get(f"{self.base_url}/encounter/{encounter_id}", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == encounter_id
            self.log("[OK] Get encounter working")
        except Exception as e:
            self.log(f"[FAIL] Get encounter failed: {e}", "ERROR")
            return False
        
        # Test get migrant encounters
        try:
            response = requests.get(f"{self.base_url}/encounter/migrant/{migrant_id}", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            self.log("[OK] Get migrant encounters working")
        except Exception as e:
            self.log(f"[FAIL] Get migrant encounters failed: {e}", "ERROR")
            return False
        
        return encounter_id
    
    def test_consent_operations(self, migrant_id):
        """Test consent operations"""
        self.log("Testing consent operations...")
        
        # Test create consent
        try:
            consent_data = {
                "migrant_id": migrant_id,
                "consent_text": "I consent to sharing my medical data"
            }
            response = requests.post(
                f"{self.base_url}/consent/",
                json=consent_data,
                headers=self.headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["migrant_id"] == migrant_id
            
            consent_id = data["id"]
            self.log(f"[OK] Consent created with ID: {consent_id}")
        except Exception as e:
            self.log(f"[FAIL] Create consent failed: {e}", "ERROR")
            return False
        
        # Test check consent status
        try:
            response = requests.get(f"{self.base_url}/consent/check/{migrant_id}", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data["has_consent"] == True
            assert data["migrant_id"] == migrant_id
            self.log("[OK] Check consent status working")
        except Exception as e:
            self.log(f"[FAIL] Check consent status failed: {e}", "ERROR")
            return False
        
        return consent_id
    
    def test_integration_services(self):
        """Test integration endpoints"""
        self.log("Testing integration services...")
        
        # Test ABHA creation
        try:
            abha_data = {
                "name": "Test User",
                "dob": "1990-01-01",
                "gender": "Male",
                "mobile": "+91-9999999999"
            }
            response = requests.post(
                f"{self.base_url}/integration/abha/create",
                json=abha_data,
                headers=self.headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "abha_id" in data
            assert data["status"] == "success"
            self.log("[OK] ABHA creation working")
        except Exception as e:
            self.log(f"[FAIL] ABHA creation failed: {e}", "ERROR")
            return False
        
        # Test Aadhaar verification
        try:
            aadhaar_data = {
                "aadhaar_number": "123456789012"
            }
            response = requests.post(
                f"{self.base_url}/integration/aadhaar/verify",
                json=aadhaar_data,
                headers=self.headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "verified" in data
            assert "message" in data
            self.log("[OK] Aadhaar verification working")
        except Exception as e:
            self.log(f"[FAIL] Aadhaar verification failed: {e}", "ERROR")
            return False
        
        # Test integration health check
        try:
            response = requests.get(f"{self.base_url}/integration/health", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            self.log("[OK] Integration health check working")
        except Exception as e:
            self.log(f"[FAIL] Integration health check failed: {e}", "ERROR")
            return False
        
        return True
    
    def test_analytics(self):
        """Test analytics endpoints"""
        self.log("Testing analytics...")
        
        # Test heatmap endpoint
        try:
            response = requests.get(f"{self.base_url}/analytics/heatmap", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "FeatureCollection"
            assert "features" in data
            self.log("[OK] Heatmap endpoint working")
        except Exception as e:
            self.log(f"[FAIL] Heatmap endpoint failed: {e}", "ERROR")
            return False
        
        # Test stats endpoint
        try:
            response = requests.get(f"{self.base_url}/analytics/stats", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert "totals" in data
            assert "by_district" in data
            self.log("[OK] Stats endpoint working")
        except Exception as e:
            self.log(f"[FAIL] Stats endpoint failed: {e}", "ERROR")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all API tests"""
        self.log(">>> Starting comprehensive API testing...")
        
        # Test health check
        if not self.test_health_check():
            return False
        
        # Test authentication
        if not self.test_authentication():
            return False
        
        # Test migrant operations
        migrant_id = self.test_migrant_operations()
        if not migrant_id:
            return False
        
        # Test encounter operations
        encounter_id = self.test_encounter_operations(migrant_id)
        if not encounter_id:
            return False
        
        # Test consent operations
        consent_id = self.test_consent_operations(migrant_id)
        if not consent_id:
            return False
        
        # Test integration services
        if not self.test_integration_services():
            return False
        
        # Test analytics
        if not self.test_analytics():
            return False
        
        self.log("[SUCCESS] All API tests passed successfully!")
        return True

def main():
    """Main function to run API tests"""
    print("=" * 60)
    print("SIH Backend - Comprehensive API Testing")
    print("=" * 60)
    
    tester = APITester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n[SUCCESS] All tests completed successfully!")
            print("\nAPI Endpoints Summary:")
            print("- Authentication: [OK] Working")
            print("- Migrant Management: [OK] Working")
            print("- Medical Encounters: [OK] Working")
            print("- Consent Management: [OK] Working")
            print("- Integration Services: [OK] Working")
            print("- Analytics: [OK] Working")
            return 0
        else:
            print("\n[FAIL] Some tests failed. Check the logs above.")
            return 1
    except KeyboardInterrupt:
        print("\n[WARN] Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
