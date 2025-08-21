#!/bin/bash
cd /root/pizero-clock/python

# Create venv if it doesn’t exist
if [ ! -d "/root/myenv" ]; then
    python3 -m venv /root/myenv
    /root/myenv/bin/pip install --upgrade pip
    /root/myenv/bin/pip install spotipy Pillow gpiozero RPi.GPIO
fi

# Activate venv and run script
exec /root/myenv/bin/python clock-spotify.py

