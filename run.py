# run.py
import subprocess
import sys
import signal
import os
import time

fastapi_process = None
streamlit_process = None

def signal_handler(sig, frame):
    print("\nShutting down services...")
    if fastapi_process:
        fastapi_process.terminate()  # Graceful shutdown
    if streamlit_process:
        streamlit_process.terminate()
    time.sleep(2)  # Give processes time to exit
    
    # Force kill if still running
    if fastapi_process and fastapi_process.poll() is None:
        fastapi_process.kill()
    if streamlit_process and streamlit_process.poll() is None:
        streamlit_process.kill()
    
    sys.exit(0)

def run_fastapi(dev_mode=False):
    global fastapi_process
    cmd = ['uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000']
    if dev_mode:
        cmd.append('--reload')
    
    # Create new process group (Unix) or job object (Windows)
    if os.name == 'posix':
        fastapi_process = subprocess.Popen(cmd, preexec_fn=os.setsid)
    else:
        fastapi_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

def run_streamlit():
    global streamlit_process
    cmd = ['streamlit', 'run', 'dashboard.py']
    if os.name == 'posix':
        streamlit_process = subprocess.Popen(cmd, preexec_fn=os.setsid)
    else:
        streamlit_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    dev_mode = '--dev' in sys.argv
    run_fastapi(dev_mode)
    run_streamlit()
    
    # Keep main process alive
    while True:
        time.sleep(1)

