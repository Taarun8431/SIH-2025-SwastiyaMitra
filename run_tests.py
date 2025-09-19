#!/usr/bin/env python3
"""
Script to start the backend server and run comprehensive API tests
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Start the server using uvicorn
    if os.name == 'nt':  # Windows
        cmd = ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    else:
        cmd = ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Server started successfully!")
        print("🌐 Server running at: http://localhost:8000")
        print("📚 API docs available at: http://localhost:8000/docs")
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_tests():
    """Run the comprehensive API tests"""
    print("\n🧪 Running comprehensive API tests...")
    
    try:
        # Wait a moment for server to fully start
        time.sleep(3)
        
        # Run the test script
        result = subprocess.run([sys.executable, "test_api.py"], 
                              capture_output=True, text=True)
        
        print("📊 Test Results:")
        print("=" * 50)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errors/Warnings:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 SIH Backend - Data Upload & Fetch Testing")
    print("=" * 60)
    
    # Start the server
    server_process = start_server()
    
    if not server_process:
        print("❌ Cannot proceed without server")
        return 1
    
    try:
        # Run the tests
        success = run_tests()
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("\n📋 Summary of operations tested:")
            print("✅ Database connection and authentication")
            print("✅ Migrant registration (data upload)")
            print("✅ Migrant data retrieval (data fetch)")
            print("✅ Medical encounter creation")
            print("✅ Encounter data retrieval")
            print("✅ Consent management")
            print("✅ Integration services (ABHA, Aadhaar)")
            print("✅ Analytics and reporting")
        else:
            print("\n❌ Some tests failed - check output above")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    finally:
        # Clean up - terminate server
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")

if __name__ == "__main__":
    sys.exit(main())
