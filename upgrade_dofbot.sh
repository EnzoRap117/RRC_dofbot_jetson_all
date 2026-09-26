#!/bin/bash

if [[ "$EUID" -ne 0 ]]; then
        echo "This script must be run as root."
        exit 1
fi

# Update all system packages
cp sources.list /etc/apt/sources.list
apt update
apt upgrade

# Install all python packages globally
sudo -H python3 -m pip install --upgrade pip
sudo -H python2 -m pip install --upgrade pip
sudo -H python3 -m pip freeze --user > requirements3.txt
sudo -H python2 -m pip freeze --user > requirements2.txt
sudo -H python3 -m pip install -r requirements3.txt
sudo -H python2 -m pip install -r requirements2.txt

# Clean up cache
# rm /root/cache

# Write skeleton structure (saved on usb)
cp skel /etc/skel

# Unzip code0 and link to it for students
unzip "/home/jetson/code0/0.Code/Jetson-dofbot-Code.zip"
ln -s "/home/jetson/code/0.Code/Jetson-dofbot-Code" /etc/skel/Desktop/readonly_examples

