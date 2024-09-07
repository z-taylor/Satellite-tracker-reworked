@echo off
setlocal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed
    for /f "tokens=*" %%i in ('choco --version') do set choco_version=%%i
    if not defined choco_version (
        echo Chocolatey is not installed. Installing Chocolatey.....
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        choco --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo Chocolatey installation failed. Exiting.....
            exit /b 1
        )
    ) else (
        echo Chocolatey is already installed
    )

    echo Installing Python via Chocolatey.....
    choco install python -y
    refreshenv
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python installation failed. Exiting.....
        exit /b 1
    )
) else (
    echo Python is already installed
)
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not in the PATH.
    for /f "usebackq tokens=*" %%i in (`python -c "import sys; print(sys.executable)"`) do set python_path=%%i
    set python_dir=%python_path%\..\
    echo Setting Python path to %python_path%
    set PATH=%python_dir%;%PATH%
) else (
    echo Python is in the PATH
)
python -m pip install --upgrade pip
python -m pip install PySide6 geocoder requests pyhigh pyproj skyfield python-dateutil pyhamlib
pause
