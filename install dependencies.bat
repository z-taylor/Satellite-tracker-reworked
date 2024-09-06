@echo off
setlocal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing.....
    winget install --id=Python.Python.3 --source=winget
    setx PATH "%PATH%;%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"
    set PATH=%PATH%;%USERPROFILE%\AppData\Local\Microsoft\WindowsApps
    echo Python has been installed
)
python -m pip install --upgrade pip
python -m pip install PySide6 geocoder requests pyhigh pyproj skyfield python-dateutil pyhamlib
pause