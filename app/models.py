from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# from geoalchemy2 import Geometry  # Temporarily disabled
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="worker")  # "admin", "doctor", "worker"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounters = relationship("Encounter", back_populates="doctor")
    consent_logs = relationship("ConsentLog", back_populates="actor")

class Migrant(Base):
    __tablename__ = "migrants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    dob = Column(DateTime, nullable=True)  # Date of birth
    gender = Column(String(10), nullable=True)
    contact = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)  # Alternative phone field
    language = Column(String(50), nullable=True)
    district = Column(String(100), nullable=True)
    district_in_kerala = Column(String(100), index=True)  # Specific Kerala district
    occupation = Column(String(100), nullable=True)
    qr_code = Column(Text, nullable=True)  # Base64 encoded QR code
    abha_id = Column(String(50), nullable=True)  # ABHA ID integration
    
    # Geospatial fields (lat/lng only, no PostGIS geometry)
    location_lat = Column(Float)
    location_lng = Column(Float)
    # location = Column(Geometry('POINT', srid=4326))  # Temporarily disabled
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounters = relationship("Encounter", back_populates="migrant")
    consents = relationship("Consent", back_populates="migrant")
    consent_logs = relationship("ConsentLog", back_populates="migrant")
    
    # Create indexes
    __table_args__ = (
        Index('idx_migrant_district', 'district_in_kerala'),
        # Index('idx_migrant_location', 'location', postgresql_using='gist'),  # Temporarily disabled
        Index('idx_migrant_abha_id', 'abha_id'),
    )

class Encounter(Base):
    __tablename__ = "encounters"
    
    id = Column(Integer, primary_key=True, index=True)
    migrant_id = Column(Integer, ForeignKey("migrants.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Medical information
    symptoms = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Encounter metadata
    encounter_type = Column(String(50), nullable=True)
    occurred_at = Column(DateTime, nullable=True)
    
    # Geospatial fields for encounter location (lat/lng only, no PostGIS geometry)
    location_lat = Column(Float)
    location_lng = Column(Float)
    # location = Column(Geometry('POINT', srid=4326))  # Temporarily disabled
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    migrant = relationship("Migrant", back_populates="encounters")
    doctor = relationship("User", back_populates="encounters")
    
    # Create indexes
    __table_args__ = (
        Index('idx_encounter_migrant_id', 'migrant_id'),
        Index('idx_encounter_doctor_id', 'doctor_id'),
        Index('idx_encounter_type', 'encounter_type'),
        Index('idx_encounter_occurred_at', 'occurred_at'),
        # Index('idx_encounter_location', 'location', postgresql_using='gist'),  # Temporarily disabled
    )

class Consent(Base):
    __tablename__ = "consents"
    
    id = Column(Integer, primary_key=True, index=True)
    migrant_id = Column(Integer, ForeignKey("migrants.id"), nullable=False)
    consent_text = Column(Text, nullable=False)
    given_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    migrant = relationship("Migrant", back_populates="consents")

class ConsentLog(Base):
    __tablename__ = "consent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    migrant_id = Column(Integer, ForeignKey("migrants.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # "granted", "revoked", "viewed"
    consented = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    migrant = relationship("Migrant", back_populates="consent_logs")
    actor = relationship("User", back_populates="consent_logs")
    
    # Create indexes
    __table_args__ = (
        Index('idx_consent_log_migrant_id', 'migrant_id'),
        Index('idx_consent_log_actor_id', 'actor_id'),
        Index('idx_consent_log_timestamp', 'timestamp'),
    )
