Grizzly Remote Control Server

The Grizzly Remote Control Server is a Python application designed to provide remote control capabilities for various system functions, such as volume control, screen management, and system shutdown. It utilizes Flask, pycaw, comtypes, and zeroconf libraries to achieve its functionality.
Features:

    Volume Control: Adjust the system's master volume level and mute/unmute the audio.
    Screen Management: Turn off the screen remotely.
    System Shutdown: Initiate a system shutdown command remotely.
    Authentication: Secure access to server functionality using HTTP Basic Authentication.
    Service Discovery: Discover and advertise services using Zeroconf.

Dependencies:

    Flask: A micro web framework for building web applications in Python.
    pycaw: Python bindings for the Windows Core Audio API.
    comtypes: Python package for accessing and manipulating COM components.
    zeroconf: A pure Python implementation of multicast DNS service discovery.

Usage:

    Install the dependencies by running the setup.bat
    Start the server by running python main-server.py.
    Access the server endpoints to control various system functions remotely.

Configuration:

    Username and password can be configured in config.txt for authentication.
    Bear name can be configured in config.txt.

Contributing:

Contributions to improve the functionality, add new features, or fix bugs are welcome! Please feel free to submit pull requests.
