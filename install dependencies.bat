@echo off
setlocal enabledelayedexpansion
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges. Please run again as an administrator
    pause
    exit /b 0
)
set "choco_path=C:\ProgramData\chocolatey\bin\choco.exe"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed
    :: Check if Chocolatey is installed
    if not exist "%choco_path%" (
        echo Chocolatey is not installed. Installing Chocolatey.....
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        if not exist "%choco_path%" (
            echo Chocolatey installation failed. Exiting.....
            pause
            exit /b 1
        )
        echo Chocolatey installed successfully
    ) else (
        echo Chocolatey is already installed
    )
    echo Installing Python via Chocolatey.....
    "%choco_path%" install python -y
    call :RefreshPath
) else (
    echo Python is already installed
)
echo Upgrading pip.....
python -m pip install --upgrade pip
echo Installing packages.....
python -m pip install PySide6 geocoder requests pyhigh pyproj skyfield python-dateutil
echo Installation complete
pause
exit /b 0
:RefreshPath
    for /f "tokens=2*" %%a in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path') do set "syspath=%%b"
    for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path') do set "userpath=%%b"
    set "PATH=%syspath%;%userpath%"
    echo PATH has been refreshed
goto :eof