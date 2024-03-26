import os
import ctypes
import string
import comtypes
import random
import socket
import json
import platform
import re
import threading
import tkinter as tk
import qrcode
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from flask_httpauth import HTTPBasicAuth
from PIL import Image, ImageTk

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'Web'),
            static_folder=os.path.join(os.path.dirname(__file__), 'Web'))
app.secret_key = os.urandom(24)  # Secret key for session management
auth = HTTPBasicAuth()

# Generate a random code at script start
random_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

login_token = random_code


def initialize_com():
    comtypes.CoInitialize()

def get_volume_control():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def setup():
    initialize_com()
    setup_auth()

def setup_auth():
    if not os.path.exists(CONFIG_FILE):
        get_config()

def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=False)

# Function to generate QR code image
def generate_qr_code_image(local_ip, port, random_code):
    login_url = f"http://{local_ip}:{port}/login?code={random_code}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(login_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    print("Login URL:", login_url)
    return img

CONFIG_FILE = "config.txt"
SERVICE_TYPE = "_grizzlyremote._tcp.local."
bear_name = ""
volume_control = None

def get_volume_control():
    comtypes.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def get_master_volume():
    volume_control = get_volume_control()
    volume = volume_control.GetMasterVolumeLevelScalar()
    return volume * 100  

def turn_screen_off():
    ctypes.windll.user32.SendMessageW(
        0xFFFF,  
        0x0112,   
        0xF170,   
        2         
    )

def shutdown_computer():
    os.system("shutdown /s /t 1")

def adjust_volume(volume):
    volume = max(0, min(volume, 100))  
    volume_control = get_volume_control()
    volume_control.SetMasterVolumeLevelScalar(volume / 100, None)  

def mute_volume():
    volume_control = get_volume_control()
    volume_control.SetMute(0, None)  

def unmute_volume():
    volume_control = get_volume_control()
    volume_control.SetMute(1, None)  

def volume_up_5_percent():
    volume_control = get_volume_control()
    current_volume = volume_control.GetMasterVolumeLevelScalar()
    new_volume = min(1.0, current_volume + 0.05)  
    volume_control.SetMasterVolumeLevelScalar(new_volume, None)

def volume_down_5_percent():
    volume_control = get_volume_control()
    current_volume = volume_control.GetMasterVolumeLevelScalar()
    new_volume = max(0.0, current_volume - 0.05)  
    volume_control.SetMasterVolumeLevelScalar(new_volume, None)

def get_config():
    global bear_name
    bear_name, username, password = read_config()
    
    if bear_name and username and password:
        return bear_name, username, password
    
    if not bear_name:
        bear_name = input("Name your Bear: ")
    if not username:
        username = input("Enter username: ")
    if not password:
        password = input("Enter password: ")

    save_config(bear_name, username, password)
    return bear_name, username, password

def save_config(bear_name, username, password):
    config_data = {
        "bearname": {
            "Bear_Name": bear_name,
            "Username": username,
            "Password": password
        }
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)
        input("Setup has been successful, press enter to close")

def read_config():
    if not os.path.exists(CONFIG_FILE):
        return None, None, None

    with open(CONFIG_FILE, "r") as f:
        config_data = json.load(f)

    bear_name = config_data.get("bearname", {}).get("Bear_Name")
    username = config_data.get("bearname", {}).get("Username")
    password = config_data.get("bearname", {}).get("Password")

    return bear_name, username, password

@auth.verify_password
def verify_password(username, password):
    if not os.path.exists(CONFIG_FILE):
        setup_auth()
    _, stored_username, stored_password = read_config()
    if username == stored_username and password == stored_password:
        return username
    
def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=False)

def start_flask_in_thread():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

def display_tkinter_interface(bear_name):
    # Get local IP
    local_ip = socket.gethostbyname(socket.gethostname())
    port= 5000

    # Generate QR code
    qr_code_img = generate_qr_code_image(local_ip, port, random_code)
    qr_code_img_path = "qr_code.png"
    qr_code_img.save(qr_code_img_path)

    # Render Tkinter interface
    root = tk.Tk()
    root.title("Grizzly Remote")
    root.geometry("400x400")

    # Set dark theme
    root.configure(bg="#121212")
    root.option_add("*TButton*background", "#1E1E1E")
    root.option_add("*TButton*foreground", "white")

    # Hi 'bear_name' Welcome Back label
    welcome_label = tk.Label(root, text=f"Hi {bear_name}, Welcome Back", font=("Helvetica", 20), fg="white", bg="#121212")
    welcome_label.pack(pady=10)

    # QR code display
    qr_code_img = Image.open(qr_code_img_path)
    qr_code_img = qr_code_img.resize((200, 200), Image.LANCZOS)
    qr_code_photo = ImageTk.PhotoImage(qr_code_img)
    qr_code_label = tk.Label(root, image=qr_code_photo, bg="#121212")
    qr_code_label.image = qr_code_photo
    qr_code_label.pack(pady=10)

    # Reminder label
    reminder_label = tk.Label(root, text="ⓘ Scan this QR code to access your Grizzly remote", font=("Helvetica", 10), fg="gray", bg="#121212")
    reminder_label.pack(pady=5)

    root.mainloop()

COMMANDS = {
    "turn_screen_off": turn_screen_off,
    "shutdown_computer": shutdown_computer,
    "adjust_volume": adjust_volume,
    "mute_volume": mute_volume,
    "unmute_volume": unmute_volume,
    "volume_up_5_percent": volume_up_5_percent,
    "volume_down_5_percent": volume_down_5_percent
}

def handle_command(command):
    match = re.match(r'adjust_volume_(\d+)', command)
    if match:
        volume = int(match.group(1))
        adjust_volume(volume)
    elif command in COMMANDS:
        COMMANDS[command]()
    else:
        print("Invalid command")

@app.route('/get_device_info')
def get_device_info():
    try:
        device_info = {
            "bear_name": bear_name,
            "device_name": platform.node(),
            "device_type": platform.system(),
            "local_ip": socket.gethostbyname(socket.gethostname())
        }
        return jsonify(device_info)
    except Exception as e:
        print("Error retrieving device info:", str(e))
        return jsonify({"error": "An error occurred while retrieving device info"}), 500
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... existing code ...
    if 'code' in request.args:
        if auth_token():
            session['authenticated'] = True  # Set a session variable
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    if 'authenticated' in session:  # Check if the user is authenticated
        volume = get_master_volume()  
        return render_template('controlAppHTML.html', volume=volume)
    else:
        return redirect(url_for('login'))


def auth_token():
    login_token = random_code # Get the session token
    code = request.args.get('code')

    print("login_token:", login_token)
    print("code:", code)

    if login_token == code:
        print('Success: Authentication successful')
        return True
    else:
        print('Failure: Authentication failed')
        return False

@app.route('/')
def baseIndex():
    return redirect(url_for('login'))

@app.route('/get_master_volume')
def get_master_volume_route():
    volume = get_master_volume()
    return str(volume)


@app.route('/get_mute_state')
def get_mute_state_route():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() == "System Sounds":
            volume = session.SimpleAudioVolume
            mute_state = volume.GetMute()
            return str(mute_state)
    return 'Error: System Sounds session not found'

@app.route('/command', methods=['POST'])
def receive_command():
    command = request.data.decode("utf-8")
    handle_command(command)
    return "Command received: " + command

from flask import jsonify

# Endpoint to fetch Grizzly remote information
@app.route('/get_grizzly_info')
def get_grizzly_info():
    try:
        grizzly_info = {
            "bear_name": bear_name,
            "device_name": socket.gethostname(),
            "device_type": platform.system(),  
            "local_ip": socket.gethostbyname(socket.gethostname())
        }
        return jsonify(grizzly_info)
    except Exception as e:
        print("Error retrieving Grizzly info:", str(e))
        return jsonify({"error": "An error occurred while retrieving Grizzly info"}), 500

def save_grizzly_info_to_file(grizzly_info):
    json_file_path = os.path.join(app.root_path, 'grizzly_info.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(grizzly_info, json_file, indent=4)

# This function is called to save the Grizzly remote information to a file
def save_grizzly_info():
    grizzly_info = fetch_grizzly_info()
    save_grizzly_info_to_file(grizzly_info)
    return "Grizzly info saved successfully!"

# Route to serve the Grizzly remote information to any page requiring it via AJAX
@app.route('/fetch_grizzly_info')
def fetch_grizzly_info():
    return get_grizzly_info()

if __name__ == "__main__":
    setup()
    print("Starting Flask in a separate thread...")
    start_flask_in_thread()
    bear_name, _, _ = get_config()  # Initialize bear_name variable
    print("Displaying Tkinter interface...")
    tk_thread = threading.Thread(target=display_tkinter_interface(bear_name))
    tk_thread.start()
    print("Flask app is running...")
    app.run(host='0.0.0.0', port=5000, threaded=False)

