# 🏥 SIH Frontend - Upload Your Own Data

This guide shows you how to upload your own data from the frontend to the database and view it physically in PostgreSQL.

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
cd "c:\Users\Taaru\OneDrive\Desktop\ABHA2.0\sih_backend"
python -m uvicorn app.main:app --reload
```

### 2. Open the Frontend
Open `frontend/index.html` in your web browser or serve it locally:
```bash
# Option 1: Double-click index.html
# Option 2: Use Python's built-in server
cd frontend
python -m http.server 8080
# Then open: http://localhost:8080
```

### 3. Upload Your Data

#### Step 1: Login
- Username: `admin`
- Password: `admin123`
- Click "Login"

#### Step 2: Register a Migrant
Fill in the form with your own data:
- **Name**: Your test name
- **Gender**: Select gender
- **Contact**: Phone number
- **District**: Select Kerala district
- **Occupation**: Job title
- **Age**: Age in years
- **Location**: Latitude/Longitude coordinates

Click "Register Migrant" to upload to database.

#### Step 3: Add Medical Encounter
- **Select Migrant**: Choose from dropdown
- **Symptoms**: Describe symptoms
- **Diagnosis**: Medical diagnosis
- **Treatment**: Treatment plan
- **Type**: Consultation/Follow-up/Emergency/Screening

Click "Add Encounter" to upload to database.

## 🗄️ View Data in Database

### Method 1: Use the Database Viewer Script
```bash
python view_database.py
```

This will show:
- ✅ Database table structure
- 👤 All users in the system
- 👥 All migrant records
- 🏥 All medical encounters
- 📊 Statistics and analytics

### Method 2: Direct PostgreSQL Access

#### Using psql (Command Line)
```bash
psql -h localhost -U postgres -d SIH-DB
```

Then run SQL queries:
```sql
-- View all migrants
SELECT * FROM migrants ORDER BY created_at DESC;

-- View all encounters
SELECT e.*, m.name as migrant_name 
FROM encounters e 
JOIN migrants m ON e.migrant_id = m.id 
ORDER BY e.created_at DESC;

-- View recent activity
SELECT 'Migrant' as type, name, created_at FROM migrants
UNION ALL
SELECT 'Encounter' as type, diagnosis, created_at FROM encounters
ORDER BY created_at DESC LIMIT 10;
```

#### Using pgAdmin (GUI)
1. Open pgAdmin
2. Connect to server: `localhost`
3. Database: `SIH-DB`
4. Browse tables: `migrants`, `encounters`, `users`, `consents`

## 📊 Real-Time Data Flow

```
Frontend Form → API Request → FastAPI Backend → PostgreSQL Database
     ↓              ↓              ↓                ↓
  User Input → JSON Payload → SQLAlchemy ORM → Physical Storage
```

## 🔍 Verify Data Upload

### 1. Frontend Verification
- Check the "Recent Data" section
- Click "Refresh Data" to see latest entries
- Verify your uploaded records appear

### 2. Database Verification
```bash
# Run the database viewer
python view_database.py

# Or check specific migrant
python -c "
from app.database import SessionLocal
from app.models import Migrant
session = SessionLocal()
latest = session.query(Migrant).order_by(Migrant.id.desc()).first()
print(f'Latest migrant: {latest.name} (ID: {latest.id})')
session.close()
"
```

### 3. API Verification
```bash
# Test the API directly
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/migrant/
```

## 🎯 Complete Example Workflow

1. **Start Backend**: `python -m uvicorn app.main:app --reload`
2. **Open Frontend**: Open `frontend/index.html`
3. **Login**: admin/admin123
4. **Add Migrant**: Fill form with your data
5. **Add Encounter**: Create medical record
6. **View in Frontend**: Check "Recent Data" section
7. **View in Database**: Run `python view_database.py`
8. **Verify Persistence**: Restart server, data remains

## 💾 Database Tables

Your data is stored in these PostgreSQL tables:

- **`migrants`**: Personal information, location, QR codes
- **`encounters`**: Medical records, symptoms, treatments
- **`users`**: System users (admin, doctor, worker)
- **`consents`**: Data sharing permissions

## 🔧 Troubleshooting

### Frontend Issues
- **CORS Error**: Make sure backend is running on port 8000
- **Login Failed**: Check username/password (admin/admin123)
- **Upload Failed**: Check browser console for errors

### Database Issues
- **Connection Failed**: Ensure PostgreSQL is running
- **No Data**: Run `python scripts/seed_data.py` first
- **Permission Error**: Check database credentials in `.env`

### Backend Issues
- **Server Won't Start**: Check if port 8000 is free
- **Import Errors**: Run `pip install -r requirements.txt`
- **Database Errors**: Check DATABASE_URL in `.env`

## 📈 Next Steps

- **Bulk Upload**: Use CSV import functionality
- **Advanced Queries**: Write custom SQL in `view_database.py`
- **API Integration**: Connect other applications to the API
- **Mobile App**: Use the same API endpoints for mobile
- **Analytics**: Use the `/analytics` endpoints for reporting

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Frontend shows "Login successful"
- ✅ Forms submit without errors
- ✅ "Recent Data" shows your entries
- ✅ `view_database.py` displays your records
- ✅ Data persists after server restart
