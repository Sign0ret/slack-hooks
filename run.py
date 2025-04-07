# run.py
import subprocess
import sys

def run_fastapi(dev_mode=False):
    if dev_mode:
        command = ['uvicorn', 'app:app', '--reload', '--host', '0.0.0.0', '--port', '8000']
    else:
        command = ['python', 'app.py']
    subprocess.Popen(command)

def run_streamlit():
    subprocess.Popen(['streamlit', 'run', 'dashboard.py'])

if __name__ == "__main__":
    dev_mode = '--dev' in sys.argv
    run_fastapi(dev_mode)
    run_streamlit()

