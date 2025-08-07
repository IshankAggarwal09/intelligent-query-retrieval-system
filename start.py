# start.py
import subprocess
import threading
import os
import time
import signal
import sys

def run_fastapi():
    """Run FastAPI backend on port 8001"""
    try:
        subprocess.run([
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ], check=True)
    except Exception as e:
        print(f"FastAPI failed to start: {e}")

def run_streamlit():
    """Run Streamlit frontend on the main PORT"""
    time.sleep(5)  # Wait for FastAPI to start
    port = os.environ.get('PORT', '8000')
    
    try:
        subprocess.run([
            "streamlit", 
            "run", 
            "app/streamlit_app.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ], check=True)
    except Exception as e:
        print(f"Streamlit failed to start: {e}")

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Intelligent Query-Retrieval System...")
    print("📡 FastAPI backend will run on port 8001")
    print("🎨 Streamlit frontend will run on main PORT")
    
    # Start FastAPI in background thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    print("⏳ Waiting for FastAPI to initialize...")
    
    # Start Streamlit (main process)
    run_streamlit()
