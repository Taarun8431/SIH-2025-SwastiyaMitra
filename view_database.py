#!/usr/bin/env python3
"""
Script to view data directly from PostgreSQL database
Shows the physical data stored in the database tables
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[0]))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app import models

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        return engine, session
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None, None

def view_table_structure():
    """Show the structure of database tables"""
    engine, session = connect_to_database()
    if not engine:
        return
    
    print("🏗️  Database Table Structure")
    print("=" * 50)
    
    try:
        # Get table information
        tables_query = """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        ORDER BY table_name, ordinal_position;
        """
        
        result = session.execute(text(tables_query))
        
        current_table = None
        for row in result:
            table_name, column_name, data_type, is_nullable = row
            
            if table_name != current_table:
                if current_table is not None:
                    print()
                print(f"📋 Table: {table_name}")
                print("-" * 30)
                current_table = table_name
            
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            print(f"  {column_name:<20} {data_type:<15} {nullable}")
        
    except Exception as e:
        print(f"❌ Error viewing table structure: {e}")
    finally:
        session.close()

def view_migrants_data():
    """View all migrant data from database"""
    engine, session = connect_to_database()
    if not session:
        return
    
    print("\n👥 Migrants Data")
    print("=" * 50)
    
    try:
        migrants = session.query(models.Migrant).all()
        
        if not migrants:
            print("No migrants found in database")
            return
        
        print(f"Total migrants: {len(migrants)}")
        print()
        
        for migrant in migrants:
            print(f"🆔 ID: {migrant.id}")
            print(f"   Name: {migrant.name}")
            print(f"   Gender: {migrant.gender}")
            print(f"   Contact: {migrant.contact or 'N/A'}")
            print(f"   District: {migrant.district_in_kerala or 'N/A'}")
            print(f"   Occupation: {migrant.occupation or 'N/A'}")
            print(f"   Age: {migrant.age or 'N/A'}")
            print(f"   Location: {migrant.location_lat}, {migrant.location_lng}" if migrant.location_lat else "   Location: N/A")
            print(f"   Created: {migrant.created_at}")
            print(f"   QR Code: {'Yes' if migrant.qr_code else 'No'}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error viewing migrants: {e}")
    finally:
        session.close()

def view_encounters_data():
    """View all encounter data from database"""
    engine, session = connect_to_database()
    if not session:
        return
    
    print("\n🏥 Medical Encounters Data")
    print("=" * 50)
    
    try:
        encounters = session.query(models.Encounter).join(models.Migrant).all()
        
        if not encounters:
            print("No encounters found in database")
            return
        
        print(f"Total encounters: {len(encounters)}")
        print()
        
        for encounter in encounters:
            print(f"🆔 Encounter ID: {encounter.id}")
            print(f"   Migrant: {encounter.migrant.name} (ID: {encounter.migrant_id})")
            print(f"   Type: {encounter.encounter_type}")
            print(f"   Symptoms: {encounter.symptoms}")
            print(f"   Diagnosis: {encounter.diagnosis}")
            print(f"   Treatment: {encounter.treatment}")
            print(f"   Notes: {encounter.notes or 'N/A'}")
            print(f"   Doctor: {encounter.doctor.username if encounter.doctor else 'N/A'}")
            print(f"   Date: {encounter.occurred_at or encounter.created_at}")
            print(f"   Created: {encounter.created_at}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error viewing encounters: {e}")
    finally:
        session.close()

def view_users_data():
    """View all user data from database"""
    engine, session = connect_to_database()
    if not session:
        return
    
    print("\n👤 Users Data")
    print("=" * 50)
    
    try:
        users = session.query(models.User).all()
        
        if not users:
            print("No users found in database")
            return
        
        print(f"Total users: {len(users)}")
        print()
        
        for user in users:
            print(f"🆔 ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Created: {user.created_at}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error viewing users: {e}")
    finally:
        session.close()

def run_custom_query():
    """Run a custom SQL query"""
    engine, session = connect_to_database()
    if not session:
        return
    
    print("\n🔍 Custom Database Queries")
    print("=" * 50)
    
    queries = [
        {
            "name": "Migrants by District",
            "query": """
                SELECT district_in_kerala, COUNT(*) as count 
                FROM migrants 
                WHERE district_in_kerala IS NOT NULL 
                GROUP BY district_in_kerala 
                ORDER BY count DESC;
            """
        },
        {
            "name": "Encounters by Type",
            "query": """
                SELECT encounter_type, COUNT(*) as count 
                FROM encounters 
                GROUP BY encounter_type 
                ORDER BY count DESC;
            """
        },
        {
            "name": "Recent Activity (Last 24 hours)",
            "query": """
                SELECT 'Migrant' as type, name as description, created_at 
                FROM migrants 
                WHERE created_at > NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 'Encounter' as type, 
                       CONCAT('ID ', id, ' - ', diagnosis) as description, 
                       created_at 
                FROM encounters 
                WHERE created_at > NOW() - INTERVAL '24 hours'
                ORDER BY created_at DESC;
            """
        }
    ]
    
    try:
        for query_info in queries:
            print(f"\n📊 {query_info['name']}")
            print("-" * 30)
            
            result = session.execute(text(query_info['query']))
            rows = result.fetchall()
            
            if rows:
                for row in rows:
                    print(f"   {' | '.join(str(col) for col in row)}")
            else:
                print("   No data found")
        
    except Exception as e:
        print(f"❌ Error running custom queries: {e}")
    finally:
        session.close()

def main():
    """Main function to display all database data"""
    print("🗄️  SIH Backend - Database Viewer")
    print("📍 Database:", DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL)
    print("⏰ Generated at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Test database connection
    engine, session = connect_to_database()
    if not session:
        print("❌ Cannot connect to database. Make sure PostgreSQL is running.")
        return
    
    print("✅ Database connection successful!")
    session.close()
    
    # View all data
    view_table_structure()
    view_users_data()
    view_migrants_data()
    view_encounters_data()
    run_custom_query()
    
    print("\n" + "=" * 60)
    print("✅ Database viewing completed!")
    print("\n💡 Tips:")
    print("- Use pgAdmin or psql to connect directly to PostgreSQL")
    print("- Database: SIH-DB")
    print("- Tables: users, migrants, encounters, consents")
    print("- Run this script anytime to see current database state")

if __name__ == "__main__":
    main()
