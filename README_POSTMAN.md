# 📋 Postman API Testing Guide

## 🚀 Quick Setup

1. **Start the FastAPI server:**
   ```bash
   venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

2. **Import into Postman:**
   - Open Postman
   - Click "Import" → "File" → Select `postman_collection.json`
   - Also import `postman_environment.json` for environment variables

## 🔑 Authentication Flow

### Step 1: Login
Run the **"Login - Admin"** request first:
- This will automatically save the JWT token to `{{access_token}}` variable
- All other requests use this token for authentication

### Available Users:
- **Admin**: `username=admin, password=admin123`
- **Doctor**: `username=doctor1, password=doctor123`
- **Worker**: `username=worker1, password=worker123`

## 📊 Testing Sequence

### 1. Basic Health Check
- **Health Check** - Test server is running
- **Root Endpoint** - Test basic API response

### 2. Authentication
- **Login - Admin** - Get JWT token (auto-saves to variable)
- **Get Current User** - Verify authentication works

### 3. Migrant Management
- **Register Migrant** - Create a new migrant record
- **Get Migrant by ID** - Retrieve migrant details
- **Update Migrant** - Modify migrant information

### 4. Medical Encounters
- **Add Medical Encounter** - Record a medical consultation
- **Get Encounter by ID** - Retrieve encounter details
- **Update Encounter** - Modify encounter information

### 5. Consent Management
- **Create Consent** - Record patient consent
- **Check Consent** - Verify consent status

### 6. Integration Services
- **Create ABHA ID** - Generate ABHA health ID
- **Verify Aadhaar** - Validate Aadhaar details
- **Upload Report** - Upload medical reports (file upload)

### 7. Analytics
- **Analytics - Heatmap** - Get GeoJSON data for mapping
- **Analytics - Stats** - Get system statistics

## 🔧 Variables Used

- `{{base_url}}` - Server URL (http://localhost:8000)
- `{{access_token}}` - JWT token (auto-populated after login)

## 📝 Sample Data

The collection includes realistic sample data for testing:
- Migrant registration with Kerala districts
- Medical encounters with symptoms/diagnosis
- Consent forms with proper text
- Integration requests with mock data

## 🚨 Important Notes

1. **Always login first** - The token expires after 30 minutes
2. **Sequential testing** - Some requests depend on previous ones (e.g., migrant ID)
3. **File uploads** - For "Upload Report", select any file in the form-data
4. **Error handling** - Check response status codes and error messages

## 🎯 Expected Responses

- **200 OK** - Successful requests
- **201 Created** - Successful creation
- **401 Unauthorized** - Invalid/expired token
- **404 Not Found** - Resource doesn't exist
- **422 Validation Error** - Invalid request data

## 🔄 Auto-Token Management

The login requests include a test script that automatically saves the JWT token:
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.collectionVariables.set('access_token', response.access_token);
    console.log('Token saved:', response.access_token);
}
```

This means you don't need to manually copy/paste tokens between requests!
