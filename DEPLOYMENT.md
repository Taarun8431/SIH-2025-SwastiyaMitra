# 🚀 Deployment Guide - Migrant Health System

This guide will help you deploy the consolidated Migrant Health System.

## ✅ Prerequisites

- **Docker** and **Docker Compose** installed.
- **Python 3.9+** (optional, for local development).

## 🐳 Quick Start (Recommended)

The easiest way to run the application is using Docker Compose. This handles the database (PostgreSQL + PostGIS) and the API server automatically.

1.  **Build and Start:**
    ```bash
    docker-compose up --build
    ```

2.  **Access the Application:**
    - API: `http://localhost:8000`
    - Documentation: `http://localhost:8000/docs`

3.  **Stop the Application:**
    ```bash
    docker-compose down
    ```

## 🛠️ Local Development Setup

If you want to run the API locally (without Docker for the app, but you still need a DB):

1.  **Set up Database:**
    You still need a PostgreSQL database with PostGIS. You can use Docker for just the DB:
    ```bash
    docker run --name migrant-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=migrant_health_db -p 5432:5432 -d postgis/postgis:15-3.3
    ```

2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
    Ensure `DATABASE_URL` matches your local DB credentials.

5.  **Run Migrations & Seed Data:**
    ```bash
    # Create tables (if not using Alembic)
    python scripts/seed_data.py
    ```

6.  **Start Server:**
    ```bash
    uvicorn app.main:app --reload
    ```

## 🧪 Testing

To run the comprehensive test suite:

```bash
python run_tests.py
```
This script will start the server and run all API tests.

## 📁 Project Structure

- `app/`: Main application code.
    - `models.py`: Database models (with PostGIS).
    - `routes/`: API endpoints.
    - `crud.py`: Database operations.
- `alembic/`: Database migrations.
- `scripts/`: Utility scripts (seeding, testing).
- `docker-compose.yml`: Docker configuration.

## 🔧 Troubleshooting

- **Database Connection Failed:** Ensure the Docker container is running. The app has a retry mechanism, so give it a few seconds.
- **PostGIS Errors:** Ensure you are using the `postgis/postgis` image, not standard `postgres`.
