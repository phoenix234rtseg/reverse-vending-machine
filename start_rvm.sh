#!/bin/bash

cd /home/pi/rvm
source venv/bin/activate
python app.py &
sleep 8
chromium \
  --kiosk \
  --disable-gpu \
  --no-sandbox \
  http://localhost:5000
