from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable, with PostGIS support
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/migrant_health_db")

# Create SQLAlchemy engine with PostGIS support
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL/PostGIS configuration
    import time
    from sqlalchemy.exc import OperationalError

    max_retries = 5
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test connection
            with engine.connect() as connection:
                break
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}/{max_retries}). Retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            else:
                print("Could not connect to database after multiple attempts.")
                raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
