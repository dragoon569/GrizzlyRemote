import subprocess
import sys
import os

def add_firewall_exception(port):
    try:
        subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=FlaskApp", "dir=in", "action=allow", f"protocol=TCP", f"localport={port}"])
        print("Firewall exception added successfully.")
    except Exception as e:
        print("Error adding firewall exception:", e)

# Call this function with the port your Flask app is running on
add_firewall_exception(5000)

def install_dependencies():
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "flask",
            "pycaw",
            "comtypes",
            "zeroconf",
            "flask_httpauth",
            "Pillow",  # Pillow is the Python Imaging Library and is required for working with images (PIL)
            "qrcode",  # qrcode library for generating QR codes
        ])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print("Error installing dependencies:", e)
        sys.exit(1)

def print_bear_art():
    os.system("cls")
    print("Setup completed successfully! Press any key to exit. You can delete the Setup.bat now")


if __name__ == "__main__":
    print("Installing dependencies...")
    install_dependencies()
    print_bear_art()

    # Wait for any key press to continue
    try:
        input()
    except KeyboardInterrupt:
        pass