#!/usr/bin/env python3
"""
Quick test script to demonstrate data upload and fetch operations
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_data_operations():
    """Test uploading and fetching data"""
    print("🎯 Testing Data Upload and Fetch Operations")
    print("=" * 50)
    
    # Step 1: Login to get authentication token
    print("1️⃣ Authenticating...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Upload migrant data
    print("\n2️⃣ Uploading migrant data...")
    migrant_data = {
        "name": "John Doe",
        "gender": "Male",
        "contact": "+91-9876543210",
        "district_in_kerala": "Ernakulam",
        "occupation": "Construction Worker",
        "location_lat": 9.9312,
        "location_lng": 76.2673
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/migrant/register",
            json=migrant_data,
            headers=headers
        )
        
        if response.status_code == 200:
            migrant_result = response.json()
            migrant_id = migrant_result["id"]
            print(f"✅ Migrant uploaded successfully with ID: {migrant_id}")
            print(f"   Name: {migrant_result['name']}")
            print(f"   District: {migrant_result['district_in_kerala']}")
            print(f"   QR Code generated: {'qr_code' in migrant_result}")
        else:
            print(f"❌ Migrant upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Migrant upload error: {e}")
        return False
    
    # Step 3: Fetch the uploaded migrant data
    print("\n3️⃣ Fetching uploaded migrant data...")
    try:
        response = requests.get(f"{BASE_URL}/migrant/{migrant_id}", headers=headers)
        
        if response.status_code == 200:
            fetched_migrant = response.json()
            print("✅ Migrant data fetched successfully:")
            print(f"   ID: {fetched_migrant['id']}")
            print(f"   Name: {fetched_migrant['name']}")
            print(f"   Gender: {fetched_migrant['gender']}")
            print(f"   Contact: {fetched_migrant['contact']}")
            print(f"   District: {fetched_migrant['district_in_kerala']}")
            print(f"   Occupation: {fetched_migrant['occupation']}")
            print(f"   Location: ({fetched_migrant['location_lat']}, {fetched_migrant['location_lng']})")
        else:
            print(f"❌ Migrant fetch failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Migrant fetch error: {e}")
        return False
    
    # Step 4: Upload encounter data
    print("\n4️⃣ Uploading medical encounter data...")
    encounter_data = {
        "migrant_id": migrant_id,
        "symptoms": "Fever, headache, body pain",
        "diagnosis": "Viral fever",
        "treatment": "Rest, paracetamol 500mg twice daily",
        "encounter_type": "consultation",
        "notes": "Patient advised to return if symptoms worsen"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/encounter/add",
            json=encounter_data,
            headers=headers
        )
        
        if response.status_code == 200:
            encounter_result = response.json()
            encounter_id = encounter_result["id"]
            print(f"✅ Encounter uploaded successfully with ID: {encounter_id}")
            print(f"   Symptoms: {encounter_result['symptoms']}")
            print(f"   Diagnosis: {encounter_result['diagnosis']}")
            print(f"   Treatment: {encounter_result['treatment']}")
        else:
            print(f"❌ Encounter upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Encounter upload error: {e}")
        return False
    
    # Step 5: Fetch encounter data
    print("\n5️⃣ Fetching uploaded encounter data...")
    try:
        response = requests.get(f"{BASE_URL}/encounter/{encounter_id}", headers=headers)
        
        if response.status_code == 200:
            fetched_encounter = response.json()
            print("✅ Encounter data fetched successfully:")
            print(f"   ID: {fetched_encounter['id']}")
            print(f"   Migrant ID: {fetched_encounter['migrant_id']}")
            print(f"   Symptoms: {fetched_encounter['symptoms']}")
            print(f"   Diagnosis: {fetched_encounter['diagnosis']}")
            print(f"   Treatment: {fetched_encounter['treatment']}")
            print(f"   Type: {fetched_encounter['encounter_type']}")
            print(f"   Date: {fetched_encounter['occurred_at']}")
        else:
            print(f"❌ Encounter fetch failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Encounter fetch error: {e}")
        return False
    
    # Step 6: Fetch all migrant encounters
    print("\n6️⃣ Fetching all encounters for the migrant...")
    try:
        response = requests.get(f"{BASE_URL}/encounter/migrant/{migrant_id}", headers=headers)
        
        if response.status_code == 200:
            encounters = response.json()
            print(f"✅ Found {len(encounters)} encounter(s) for migrant:")
            for i, enc in enumerate(encounters, 1):
                date_str = enc.get('occurred_at', 'Unknown')
                if date_str and date_str != 'Unknown':
                    try:
                        date_display = date_str[:10] if len(date_str) >= 10 else date_str
                    except (TypeError, AttributeError):
                        date_display = 'Unknown'
                else:
                    date_display = 'Unknown'
                print(f"   {i}. {enc['encounter_type']} - {enc['diagnosis']} ({date_display})")
        else:
            print(f"❌ Fetch migrant encounters failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Fetch migrant encounters error: {e}")
        return False
    
    # Step 7: List all migrants
    print("\n7️⃣ Fetching all migrants from database...")
    try:
        response = requests.get(f"{BASE_URL}/migrant/", headers=headers)
        
        if response.status_code == 200:
            migrants = response.json()
            print(f"✅ Total migrants in database: {len(migrants)}")
            print("   Recent migrants:")
            for migrant in migrants[-3:]:  # Show last 3 migrants
                print(f"   - {migrant['name']} ({migrant['district_in_kerala']})")
        else:
            print(f"❌ Fetch all migrants failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Fetch all migrants error: {e}")
        return False
    
    print("\n🎉 Data upload and fetch operations completed successfully!")
    print("\n📊 Summary:")
    print("✅ Successfully uploaded migrant data to database")
    print("✅ Successfully fetched migrant data from database")
    print("✅ Successfully uploaded encounter data to database")
    print("✅ Successfully fetched encounter data from database")
    print("✅ Successfully retrieved all related records")
    print("✅ Data persistence verified across operations")
    
    return True

def main():
    """Main function"""
    print("🚀 SIH Backend - Data Upload & Fetch Test")
    print("📍 Server: http://localhost:8000")
    print("⏰ Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Test server connectivity first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print("❌ Server responded with error:", response.status_code)
            return 1
    except Exception as e:
        print("❌ Cannot connect to server:", e)
        print("💡 Make sure the server is running: uvicorn app.main:app --reload")
        return 1
    
    # Run the data operations test
    success = test_data_operations()
    
    if success:
        print("\n🎯 All data operations completed successfully!")
        return 0
    else:
        print("\n❌ Some operations failed - check the output above")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
