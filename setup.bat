@echo off
echo Running setup with elevated privileges...
echo Please enter the administrator password when prompted.

:: Execute Python script with elevated privileges
powershell -Command "Start-Process python -ArgumentList 'requirements.py' -Verb RunAs"

