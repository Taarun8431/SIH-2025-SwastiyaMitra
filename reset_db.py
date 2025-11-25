from app.database import engine
from app.models import Base
from sqlalchemy import text

def reset_database():
    print("⚠️  WARNING: This will delete all data in the database!")
    print("🔄 Dropping all tables...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Also drop alembic_version table if it exists
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
            conn.commit()
        except Exception as e:
            print(f"Note: Could not drop alembic_version: {e}")

    print("✅ Tables dropped.")
    
    print("🔄 Recreating tables...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recreated with new schema.")

if __name__ == "__main__":
    reset_database()
