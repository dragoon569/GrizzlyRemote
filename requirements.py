import subprocess
import os

def add_firewall_exception(port):
    try:
        subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=FlaskApp", "dir=in", "action=allow", f"protocol=TCP", f"localport={port}"])
        print("Firewall exception added successfully.")
    except Exception as e:
        print("Error adding firewall exception:", e)

# Call this function with the port your Flask app is running on
add_firewall_exception(5000)


def install(package):
    os.system(f"pip install {package}")

libraries = [
    "comtypes",
    "qrcode",
    "flask",
    "pycaw",
    "flask_httpauth",
    "PIL"
]

for library in libraries:
    install(library)

def print_bear_art():
    os.system("cls")
    print("Setup completed successfully! Press any key to exit. You can delete the Setup.bat now")


if __name__ == "__main__":
    print("Installing dependencies...")
    install(libraries)
    print_bear_art()

    # Wait for any key press to continue
    try:
        input()
    except KeyboardInterrupt:
        pass