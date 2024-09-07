#!/bin/bash
command_exists() {
    command -v "$1" >/dev/null 2>&1
}
install_python_and_pip() {
    echo "Installing Python and pip....."
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip
    elif command_exists pacman; then
        sudo pacman -Syu --noconfirm python python-pip
    else
        echo "Package manager is not supported. Please manually install Python and pip"
        exit 1
    fi
    echo "Python and pip installed"
}
if ! command_exists python3; then
    echo "Python is not installed"
    install_python_and_pip
else
    echo "Python is already installed"
fi
if ! command_exists pip3; then
    echo "pip is not installed. Installing....."
    install_python_and_pip
else
    echo "pip is already installed"
fi
python3 -m pip install --upgrade pip --break-system-packages
pip3 install --break-system-packages PySide6 geocoder requests pyhigh pyproj skyfield python-dateutil pyhamlib
echo "Press enter to continue....."
read
