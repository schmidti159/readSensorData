#!/bin/bash

cd /home/pi/readSensorData
source .venv/bin/activate
while :
do
    echo "starting scipt in 60 seconds"
    sleep 60
    ./readSensorData.py
done
