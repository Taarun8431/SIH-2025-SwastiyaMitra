#!/usr/bin/env python3
"""
Setup script for SIH Backend
Automates the setup process for the integrated migrant health system
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, executable='/bin/bash')
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print("✅ Python version OK")
    
    # Check if PostgreSQL is available
    try:
        subprocess.run("psql --version", shell=True, check=True, capture_output=True)
        print("✅ PostgreSQL is available")
    except subprocess.CalledProcessError:
        print("⚠️  PostgreSQL not found. You'll need to set up the database manually.")
    
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not os.path.exists("venv"):
        return run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")
        return True

def install_dependencies():
    """Install Python dependencies"""
    # First upgrade pip
    if os.name == 'nt':  # Windows
        pip_upgrade = "venv\\Scripts\\python.exe -m pip install --upgrade pip"
        pip_install = "venv\\Scripts\\python.exe -m pip install -r requirements.txt"
    else:  # Unix/Linux/Mac
        pip_upgrade = "venv/bin/python -m pip install --upgrade pip"
        pip_install = "venv/bin/python -m pip install -r requirements.txt"
    
    if not run_command(pip_upgrade, "Upgrading pip"):
        return False
    
    return run_command(pip_install, "Installing dependencies")

def setup_environment():
    """Set up environment variables"""
    if not os.path.exists(".env"):
        print("🔄 Creating .env file from template...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                content = src.read()
                # Replace with more secure defaults
                content = content.replace("your-secret-key-change-this-in-production", 
                                        "sih-backend-secret-key-2024")
                dst.write(content)
            print("✅ .env file created")
            print("⚠️  Please update DATABASE_URL in .env with your actual database credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
        return True

def initialize_database():
    """Initialize database with Alembic"""
    print("🔄 Initializing database...")
    
    # Check if alembic directory exists
    if not os.path.exists("alembic/versions"):
        os.makedirs("alembic/versions", exist_ok=True)
    
    if os.name == 'nt':  # Windows
        alembic_cmd = "venv\\Scripts\\python.exe -m alembic"
    else:  # Unix/Linux/Mac
        alembic_cmd = "venv/bin/python -m alembic"
    
    # Create initial migration if none exists
    versions_dir = Path("alembic/versions")
    if not any(versions_dir.glob("*.py")):
        if not run_command(f"{alembic_cmd} revision --autogenerate -m \"Initial migration\"", 
                          "Creating initial migration"):
            return False
    
    # Run migrations
    return run_command(f"{alembic_cmd} upgrade head", "Running database migrations")

def seed_database():
    """Seed database with initial data"""
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python.exe"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} scripts/seed_data.py", "Seeding database with initial data")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 SIH Backend Setup Script")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup steps
    steps = [
        (setup_virtual_environment, "Virtual Environment"),
        (install_dependencies, "Dependencies"),
        (setup_environment, "Environment Variables"),
        (initialize_database, "Database"),
        (seed_database, "Sample Data")
    ]
    
    failed_steps = []
    
    for step_func, step_name in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 60)
    if failed_steps:
        print("⚠️  Setup completed with some issues:")
        for step in failed_steps:
            print(f"   ❌ {step}")
        print("\nPlease resolve the issues above and run the setup again.")
        print("You can also set up these components manually.")
    else:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update DATABASE_URL in .env with your PostgreSQL credentials")
        print("2. Run: uvicorn app.main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
        print("\nDefault users:")
        print("- Admin: username=admin, password=admin123")
        print("- Doctor: username=doctor1, password=doctor123")
        print("- Worker: username=worker1, password=worker123")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
