import os
import ctypes
import socket
import json
import subprocess
import platform
import re
import threading
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from flask_httpauth import HTTPBasicAuth
from zeroconf import IPVersion, ServiceInfo, Zeroconf, ServiceBrowser

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'Web'),
            static_folder=os.path.join(os.path.dirname(__file__), 'Web'))
app.secret_key = os.urandom(24)  # Secret key for session management
auth = HTTPBasicAuth()

CONFIG_FILE = "config.txt"
SERVICE_TYPE = "_grizzlyremote._tcp.local."
BEAR_NAME = ""
volume_control = None
discovered_peers = []  # List to store discovered peers' information


def get_bear_name():
    global BEAR_NAME
    bear_name = read_config()[0]  # Read bear name from config file
    if bear_name:
        BEAR_NAME = bear_name
    else:
        BEAR_NAME = input("Name your Bear: ")
        with open(CONFIG_FILE, "w") as f:
            f.write(f"{BEAR_NAME}\n")

def get_username_password():
    username = input("Enter username: ")
    password = input("Enter password: ")
    with open(CONFIG_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

def read_config():
    if not os.path.exists(CONFIG_FILE):
        return None, None, None
    with open(CONFIG_FILE, "r") as f:
        lines = f.readlines()
        bear_name = lines[0].strip()
        if len(lines) > 1:
            username, password = lines[1].strip().split(":")
            return bear_name, username, password
        else:
            return bear_name, None, None

def setup_auth():
    if not os.path.exists(CONFIG_FILE):
        get_bear_name()
        get_username_password()

@auth.verify_password
def verify_password(username, password):
    if not os.path.exists(CONFIG_FILE):
        setup_auth()
    _, stored_username, stored_password = read_config()
    if username == stored_username and password == stored_password:
        return username

def get_volume_control():
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

def advertise_service(zc, port):
    global BEAR_NAME
    desc = {'username': read_config()[1], 'bear_name': BEAR_NAME}  
    info = ServiceInfo(type_=SERVICE_TYPE,
                       name=f"{socket.gethostname()}._grizzlyremote._tcp.local.",
                       server="",
                       addresses=[socket.inet_pton(socket.AF_INET, socket.gethostbyname(socket.gethostname()))],
                       port=port,
                       properties=desc)
    zc.register_service(info)

def browse_services(zc):
    class ServiceListener:
        def __init__(self):
            pass

        def remove_service(self, zc, type, name):
            pass

        def add_service(self, zc, type, name):
            info = zc.get_service_info(type, name)
            if info:
                print(f"Discovered service: {name} - {info.addresses[0]}")
                discovered_peers.append({"name": name, "address": socket.inet_ntoa(info.addresses[0])})

        def update_service(self, zc, type, name):
            pass

    listener = ServiceListener()
    browser = ServiceBrowser(zc, SERVICE_TYPE, listener)

def handle_discovery(zc):
    advertise_service(zc, 5000)  # Advertise own service
    browse_services(zc)  # Browse for other services

def establish_peer_connections():
    for peer in discovered_peers:
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer["address"], 5000))  # Connect to peer's service port
            # Exchange some dummy data with the peer
            message = "Hello from Grizzly Remote!"
            peer_socket.sendall(message.encode())
            response = peer_socket.recv(1024)
            print(f"Received response from {peer['name']}: {response.decode()}")
        except Exception as e:
            print(f"Error connecting to {peer['name']}: {e}")
        finally:
            peer_socket.close()

# Thread for handling service discovery and peer connections
def discovery_and_connection_thread():
    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
    handle_discovery(zeroconf)  # Perform service discovery
    establish_peer_connections()  # Establish peer connections

# Start the discovery and connection thread
discovery_thread = threading.Thread(target=discovery_and_connection_thread)
discovery_thread.start()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the username and password from the form data
        username = request.form['username']
        password = request.form['password']
        
        # Perform authentication logic here
        if verify_password(username, password):
            # Authentication successful, store user information in session
            session['username'] = username
            return redirect(url_for('home'))  # Redirect to the home page after successful login
        else:
            # Authentication failed, redirect back to the login page
            return redirect(url_for('login'))

    # If the request method is GET or authentication failed, render the login page
    return render_template('login.html')

@app.route('/')
def baseIndex():
    return redirect(url_for('login'))

@app.route('/get_master_volume')
def get_master_volume_route():
    volume = get_master_volume()
    return str(volume)


@app.route('/home')
def home():
    if 'username' in session:  # Check if the user is logged in
        volume = get_master_volume()  
        return render_template('controlAppHTML.html', volume=volume)
    else:
        return redirect(url_for('login'))

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
            "bear_name": BEAR_NAME,
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
    import comtypes
    comtypes.CoInitialize()  
    setup_auth()
    
    app.run(host='0.0.0.0', port=5000, threaded=False)
