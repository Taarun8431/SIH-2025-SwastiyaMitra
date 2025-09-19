#!/usr/bin/env python3
"""
Manual dependency installer for SIH Backend
Installs packages one by one to avoid compilation issues
"""

import subprocess
import sys
import os

def install_package(package, description=""):
    """Install a single package"""
    print(f"🔄 Installing {package}...")
    try:
        if os.name == 'nt':  # Windows
            cmd = f"venv\\Scripts\\python.exe -m pip install {package}"
        else:
            cmd = f"venv/bin/python -m pip install {package}"
        
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install packages in order of dependency"""
    print("🔄 Installing dependencies manually...")
    
    # Core packages first
    packages = [
        "wheel",
        "setuptools",
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "python-multipart==0.0.6",
        "pydantic==2.5.2",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "sqlalchemy==2.0.23",
        "alembic==1.13.1",
        "psycopg2-binary==2.9.9",
        "geoalchemy2==0.14.2",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "qrcode==7.4.2",
        "pillow==10.0.1",
        "httpx==0.25.2",
        "requests==2.31.0",
        "pytest==7.4.3"
    ]
    
    # Try to install pandas last (optional)
    optional_packages = [
        "pandas==2.0.3"
    ]
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    # Try optional packages
    for package in optional_packages:
        if not install_package(package):
            print(f"⚠️  Optional package {package} failed - CSV loading will be disabled")
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        return False
    else:
        print("\n✅ All core dependencies installed successfully!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
