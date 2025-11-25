# SIH-2025-SwastiyaMitra

A digital health record system for Kerala’s migrant population, ensuring secure medical history, multilingual access, AI-powered preventive healthcare chatbot, role-based provider access, and analytics for disease surveillance. Fully containerized with Docker for fast, scalable deployment.

## Backend Overview

Integrated FastAPI backend for migrant health management with PostGIS support, combining features from three separate backend implementations.

## Features

- **Authentication & Authorization**: JWT-based auth with role-based access control (admin, doctor, worker)
- **Migrant Management**: Registration, QR code generation, CRUD operations with geospatial support
- **Medical Encounters**: Doctor-patient encounter tracking with consent management
- **Consent System**: Comprehensive consent logging and tracking
- **Integration Services**: Mock ABHA/Aadhaar integration, file uploads, notifications
- **Analytics**: Heatmap data with GeoJSON support for district and cluster views
- **PostGIS Support**: Geospatial queries and location-based analytics

## Project Structure

```
sih_backend/
├── app/
│   ├── main.py                 # FastAPI app with all routes
│   ├── database.py             # SQLAlchemy + PostGIS engine
│   ├── models.py               # User, Migrant, Encounter, Consent models
│   ├── schemas.py              # Pydantic models for validation
│   ├── crud.py                 # Database helper functions
│   ├── auth.py                 # JWT, role-based checks, security
│   ├── utils/
│   │   └── qr_utils.py         # QR code generator (base64)
│   └── routes/
│       ├── auth_routes.py      # Authentication endpoints
│       ├── migrant_routes.py   # Migrant management
│       ├── encounter_routes.py # Medical encounters
│       ├── consent_routes.py   # Consent management
│       ├── integration_routes.py # ABHA/Aadhaar/uploads
│       ├── analytics_routes.py # Heatmap & statistics
├── alembic/                    # Database migrations
├── scripts/
│   └── seed_data.py            # Database seeding script
├── data/
│   └── districts_kerala.json   # Kerala districts GeoJSON
├── requirements.txt
├── .env.example
└── README.md
```

## Installation & Deployment

> [!IMPORTANT]
> **Please refer to [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup instructions.**

### Quick Start (Docker)

1.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
2.  **Access**: `http://localhost:8000`

For local development without Docker, see `DEPLOYMENT.md`.

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Set up PostgreSQL with PostGIS**:
   ```sql
   CREATE DATABASE migrant_health_db;
   CREATE EXTENSION postgis;
   ```

## Database Setup

1. **Initialize Alembic** (if not already done):
   ```bash
   alembic init alembic
   ```

2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Seed database with sample data**:
   ```bash
   python scripts/seed_data.py
   ```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Default Users

After running the seed script, these users will be available:

- **Admin**: `username=admin, password=admin123`
- **Doctor**: `username=doctor1, password=doctor123`
- **Worker**: `username=worker1, password=worker123`

## API Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info
- `POST /auth/register` - Register new user (admin only)

### Migrant Management
- `POST /migrant/register` - Register migrant with QR code
- `GET /migrant/{id}` - Get migrant details (with consent check)
- `PUT /migrant/{id}` - Update migrant info
- `DELETE /migrant/{id}` - Delete migrant (admin only)
- `GET /migrant/{id}/qr` - Get migrant QR code

### Medical Encounters
- `POST /encounter/add` - Add encounter (doctor/admin only)
- `GET /encounter/{id}` - Get encounter details
- `PUT /encounter/{id}` - Update encounter
- `GET /encounter/migrant/{migrant_id}` - Get migrant's encounters

### Consent Management
- `POST /consent/` - Create consent record
- `GET /consent/migrant/{migrant_id}` - Get migrant consents
- `PUT /consent/{id}/revoke` - Revoke consent
- `GET /consent/check/{migrant_id}` - Check consent status

### Integration Services
- `POST /integration/abha/create` - Create ABHA ID (mock)
- `POST /integration/aadhaar/verify` - Verify Aadhaar (mock)
- `POST /integration/upload-report` - Upload medical files
- `POST /integration/notify/sms` - Send SMS (mock)
- `POST /integration/notify/email` - Send email (mock)

### Analytics
- `GET /analytics/heatmap` - Get GeoJSON heatmap data
- `GET /analytics/stats` - Get system statistics
- `GET /analytics/trends` - Get trend data (doctor/admin only)

## Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/migrant_health_db

# JWT Configuration
JWT_SECRET=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
APP_NAME=SIH Backend - Migrant Health System
ALGORITHM=HS256
```

## Testing

The API includes comprehensive error handling and validation. Test the endpoints using:

1. **FastAPI Interactive Docs**: Visit `/docs` for interactive testing
2. **Postman/Thunder Client**: Import the API schema from `/openapi.json`
3. **curl**: Example login request:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin123"
   ```

## Key Features

### Geospatial Support
- PostGIS integration for location-based queries
- Automatic geometry creation from lat/lng coordinates
- Spatial indexing for performance
- GeoJSON output for mapping applications

### Security
- JWT token-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Input validation with Pydantic

### Consent Management
- Comprehensive consent tracking
- Action logging (granted, revoked, viewed)
- Privacy-first approach to data access

### QR Code Generation
- Automatic QR code generation for migrants
- Base64 encoded for easy display
- Regeneration capability

## Development

### Adding New Endpoints
1. Create route in appropriate `routes/` file
2. Add Pydantic schemas in `schemas.py`
3. Add CRUD functions in `crud.py`
4. Update models if needed in `models.py`

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Production Deployment

1. Set secure environment variables
2. Use production database (PostgreSQL with PostGIS)
3. Configure CORS origins appropriately
4. Use production WSGI server (gunicorn)
5. Set up SSL/TLS
6. Configure logging and monitoring

## License

This project is part of the Smart India Hackathon (SIH) initiative.
