import subprocess
import sys

def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "pycaw", "comtypes", "zeroconf", "flask_httpauth"])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print("Error installing dependencies:", e)
        sys.exit(1)

def run_server():
    try:
        subprocess.check_call([sys.executable, "main-server.py"])
    except subprocess.CalledProcessError as e:
        print("Error running server:", e)
        sys.exit(1)

if __name__ == "__main__":
    print("Installing dependencies...")
    install_dependencies()
    print("Running server...")
    run_server()
