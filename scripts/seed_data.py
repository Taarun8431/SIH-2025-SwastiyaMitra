#!/usr/bin/env python3
"""
Seed data script for SIH Backend
Populates the database with initial data from CSV files and creates default users
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, crud, schemas
from app.auth import get_password_hash

# Optional pandas import - only use if available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas not available - CSV loading will be skipped")

def create_default_users(db: Session):
    """Create default admin and doctor users"""
    print("Creating default users...")
    
    # Create admin user
    admin_user = schemas.UserCreate(
        username="admin",
        password="admin123",
        role="admin"
    )
    
    existing_admin = crud.get_user_by_username(db, "admin")
    if not existing_admin:
        crud.create_user(db, admin_user)
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")
    
    # Create doctor user
    doctor_user = schemas.UserCreate(
        username="doctor1",
        password="doctor123",
        role="doctor"
    )
    
    existing_doctor = crud.get_user_by_username(db, "doctor1")
    if not existing_doctor:
        crud.create_user(db, doctor_user)
        print("✓ Doctor user created (username: doctor1, password: doctor123)")
    else:
        print("✓ Doctor user already exists")
    
    # Create worker user
    worker_user = schemas.UserCreate(
        username="worker1",
        password="worker123",
        role="worker"
    )
    
    existing_worker = crud.get_user_by_username(db, "worker1")
    if not existing_worker:
        crud.create_user(db, worker_user)
        print("✓ Worker user created (username: worker1, password: worker123)")
    else:
        print("✓ Worker user already exists")

def load_migrants_from_csv(db: Session, csv_path: str):
    """Load migrants from CSV file"""
    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available - skipping CSV loading")
        return
        
    if not os.path.exists(csv_path):
        print(f"⚠ Migrants CSV file not found: {csv_path}")
        return
    
    print(f"Loading migrants from {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        created_count = 0
        
        for _, row in df.iterrows():
            # Create migrant data
            migrant_data = {
                "name": row.get("name", "Unknown"),
                "gender": row.get("gender", "Unknown"),
                "contact": row.get("contact", None),
                "phone": row.get("phone", None),
                "district_in_kerala": row.get("district_in_kerala", None),
                "occupation": row.get("occupation", None),
                "location_lat": row.get("location_lat", None),
                "location_lng": row.get("location_lng", None)
            }
            
            # Handle date of birth
            if "dob" in row and pd.notna(row["dob"]):
                try:
                    migrant_data["dob"] = pd.to_datetime(row["dob"])
                except:
                    migrant_data["dob"] = None
            
            migrant = schemas.MigrantCreate(**migrant_data)
            crud.create_migrant(db, migrant)
            created_count += 1
        
        print(f"✓ Created {created_count} migrants from CSV")
        
    except Exception as e:
        print(f"✗ Error loading migrants CSV: {e}")

def load_encounters_from_csv(db: Session, csv_path: str):
    """Load encounters from CSV file"""
    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available - skipping CSV loading")
        return
        
    if not os.path.exists(csv_path):
        print(f"⚠ Encounters CSV file not found: {csv_path}")
        return
    
    print(f"Loading encounters from {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        created_count = 0
        
        # Get doctor user for encounters
        doctor = crud.get_user_by_username(db, "doctor1")
        if not doctor:
            print("✗ Doctor user not found, cannot create encounters")
            return
        
        for _, row in df.iterrows():
            # Create encounter data
            encounter_data = {
                "migrant_id": row.get("migrant_id", 1),  # Default to first migrant
                "symptoms": row.get("symptoms", ""),
                "diagnosis": row.get("diagnosis", ""),
                "treatment": row.get("treatment", ""),
                "notes": row.get("notes", ""),
                "encounter_type": row.get("encounter_type", "consultation"),
                "location_lat": row.get("location_lat", None),
                "location_lng": row.get("location_lng", None)
            }
            
            # Handle occurred_at date
            if "occurred_at" in row and pd.notna(row["occurred_at"]):
                try:
                    encounter_data["occurred_at"] = pd.to_datetime(row["occurred_at"])
                except:
                    encounter_data["occurred_at"] = datetime.now()
            else:
                encounter_data["occurred_at"] = datetime.now()
            
            encounter = schemas.EncounterCreate(**encounter_data)
            crud.create_encounter(db, encounter, doctor_id=doctor.id)
            created_count += 1
        
        print(f"✓ Created {created_count} encounters from CSV")
        
    except Exception as e:
        print(f"✗ Error loading encounters CSV: {e}")

def create_sample_data(db: Session):
    """Create sample data if CSV files are not available"""
    print("Creating sample data...")
    
    # Sample districts in Kerala
    kerala_districts = [
        "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
        "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
        "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
    ]
    
    # Create sample migrants
    sample_migrants = [
        {
            "name": "Ravi Kumar",
            "gender": "Male",
            "contact": "+91-9876543210",
            "district_in_kerala": "Ernakulam",
            "occupation": "Construction Worker",
            "location_lat": 9.9312,
            "location_lng": 76.2673
        },
        {
            "name": "Priya Sharma",
            "gender": "Female", 
            "contact": "+91-9876543211",
            "district_in_kerala": "Thiruvananthapuram",
            "occupation": "Domestic Helper",
            "location_lat": 8.5241,
            "location_lng": 76.9366
        },
        {
            "name": "Mohammed Ali",
            "gender": "Male",
            "contact": "+91-9876543212",
            "district_in_kerala": "Kozhikode",
            "occupation": "Fisherman",
            "location_lat": 11.2588,
            "location_lng": 75.7804
        }
    ]
    
    created_migrants = []
    for migrant_data in sample_migrants:
        migrant = schemas.MigrantCreate(**migrant_data)
        db_migrant = crud.create_migrant(db, migrant)
        created_migrants.append(db_migrant)
    
    print(f"✓ Created {len(created_migrants)} sample migrants")
    
    # Create sample encounters
    doctor = crud.get_user_by_username(db, "doctor1")
    if doctor and created_migrants:
        sample_encounters = [
            {
                "migrant_id": created_migrants[0].id,
                "symptoms": "Fever, headache",
                "diagnosis": "Viral fever",
                "treatment": "Rest, paracetamol",
                "encounter_type": "consultation"
            },
            {
                "migrant_id": created_migrants[1].id,
                "symptoms": "Cough, cold",
                "diagnosis": "Upper respiratory infection",
                "treatment": "Antibiotics, rest",
                "encounter_type": "follow-up"
            }
        ]
        
        for encounter_data in sample_encounters:
            encounter = schemas.EncounterCreate(**encounter_data)
            crud.create_encounter(db, encounter, doctor_id=doctor.id)
        
        print(f"✓ Created {len(sample_encounters)} sample encounters")

def main():
    """Main function to seed the database"""
    print("🌱 Starting database seeding...")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create default users
        create_default_users(db)
        
        # Try to load data from CSV files only if pandas is available
        migrants_loaded = False
        if PANDAS_AVAILABLE:
            data_dir = Path(__file__).parent.parent / "data"
            migrants_csv = data_dir / "migrants.csv"
            encounters_csv = data_dir / "encounters.csv"
            
            if migrants_csv.exists():
                load_migrants_from_csv(db, str(migrants_csv))
                migrants_loaded = True
            
            if encounters_csv.exists():
                load_encounters_from_csv(db, str(encounters_csv))
        
        # Create sample data if no CSV data was loaded
        if not migrants_loaded:
            create_sample_data(db)
        
        print("🎉 Database seeding completed successfully!")
        print("\nDefault users created:")
        print("- Admin: username=admin, password=admin123")
        print("- Doctor: username=doctor1, password=doctor123")
        print("- Worker: username=worker1, password=worker123")
        
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
