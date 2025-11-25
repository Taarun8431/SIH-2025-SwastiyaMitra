import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("=" * 60)
    print("🚀 Starting SIH Migrant Health System")
    print("=" * 60)
    
    # Get current directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Start Backend
    print("\n🔌 Starting Backend Server (Port 8000)...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    backend = subprocess.Popen(
        backend_cmd,
        cwd=base_dir,
        shell=True if os.name == 'nt' else False
    )
    
    # Start Frontend
    print("💻 Starting Frontend Server (Port 3000)...")
    frontend_dir = os.path.join(base_dir, "frontend")
    frontend_cmd = [sys.executable, "-m", "http.server", "3000"]
    frontend = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        shell=True if os.name == 'nt' else False
    )
    
    # Wait for servers to initialize
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    # Open Browser
    url = "http://localhost:3000"
    print(f"🌐 Opening {url} in your browser...")
    webbrowser.open(url)
    
    print("\n✅ Application is running!")
    print("📝 Backend API: http://localhost:8000/docs")
    print("🖥️  Frontend UI: http://localhost:3000")
    print("🛡️  Admin Panel: http://localhost:3000/admin.html")
    print("\n⚠️  Press Ctrl+C to stop both servers")
    
    try:
        # Keep the script running
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend.terminate()
        frontend.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
