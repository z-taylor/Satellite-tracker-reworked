@echo off
setlocal EnableDelayedExpansion
set "WINGET_PATH=%LocalAppData%\Microsoft\WindowsApps\winget.exe"
if not exist "%WINGET_PATH%" (
    echo winget is not installed. Installing winget.....
    curl -L -o "%TEMP%\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle" "https://github.com/microsoft/winget-cli/releases/download/v1.8.1791/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    echo Installing the App Installer package...
    powershell.exe -Command "Add-AppxPackage -Path '%TEMP%\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'"
    del "%TEMP%\Microsoft.VCLibs.x64.14.00.Desktop.appx"
    del "%TEMP%\Microsoft.UI.Xaml.2.7.x64.appx"
    del "%TEMP%\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    if exist "%WINGET_PATH%" (
        echo winget has been installed successfully.
        echo Checking winget version.....
        "%WINGET_PATH%" --version
    ) else (
        echo winget installation failed. Please restart your computer and try again.
        pause
        exit /b 1
    )
)
set "PYTHON_LOCATIONS=C:\Python311;C:\Program Files\Python311;C:\Users\Zachary\AppData\Local\Programs\Python\Python311;%ProgramFiles%\Python311;%ProgramFiles(x86)%\Python311"
for %%i in ("%PYTHON_LOCATIONS:;=" "%") do (
    set "location=%%~i"
    if exist "!location!\python.exe" (
        set "PYTHON_PATH=!location!\python.exe"
        echo Python found at: !PYTHON_PATH!
        goto :found_python
    )
)
:not_found_python
echo Python not found in common locations. Attempting to install......
"%WINGET_PATH%" install --id=Python.Python.3.11 --source=winget
if %errorlevel% neq 0 (
    echo Failed to install Python. Please install manually from https://www.python.org/downloads/. Please make to check the box that says "Add Python to PATH"
    pause
    exit /b 1
)
timeout /t 10 /nobreak >nul
set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
:found_python
for %%F in ("%PYTHON_PATH%") do set "PYTHON_DIR=%%~dpF"
setx PATH "%PATH%;%PYTHON_DIR%;%PYTHON_DIR%Scripts" /M
set "PATH=%PATH%;%PYTHON_DIR%;%PYTHON_DIR%Scripts"
"%PYTHON_PATH%" --version
if %errorlevel% neq 0 (
    echo Python installation failed. Exiting.....
    pause
    exit /b 1
)
"%PYTHON_PATH%" -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Pip upgrade failed. Exiting.....
    pause
    exit /b 1
)
"%PYTHON_PATH%" -m pip install PySide6 geocoder requests pyhigh pyproj skyfield python-dateutil pyhamlib
if %errorlevel% neq 0 (
    echo Package installation failed. Exiting.....
    pause
    exit /b 1
)
pause
