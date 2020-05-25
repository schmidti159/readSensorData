#!/usr/bin/env python3

import sys
import os
import serial
import re
from datetime import datetime
from influxdb import InfluxDBClient
from dotenv import load_dotenv
load_dotenv(verbose=True)

#constants
INTERVAL = "60"

POSITION = "Position"
OUTER = "Außen"
MIDDLE = "Mitte"
INNER = "Innen"
FLOOR = "Etage"
UPPER_FLOOR = "OG"
GROUND_FLOOR = "EG"
DIRECTION = "Ausrichtung"
SOUTH = "Süd"
WEST = "West"

#tag configuration. Depends on the order of the values in the input
TAGS = [
    [INNER,  GROUND_FLOOR, SOUTH], # 01
#    [OUTER,  GROUND_FLOOR, SOUTH], # 02
#    [OUTER,  GROUND_FLOOR, WEST],  # 03
    [MIDDLE, GROUND_FLOOR, SOUTH], # 04
#    [MIDDLE, GROUND_FLOOR, WEST],  # 05
#    [OUTER,  GROUND_FLOOR, WEST],  # 06
#    [INNER,  UPPER_FLOOR,  WEST],  # 07
    [INNER,  UPPER_FLOOR,  SOUTH], # 08
    [MIDDLE, UPPER_FLOOR,  SOUTH], # 09
    [OUTER,  UPPER_FLOOR,  SOUTH] # 10
#    [INNER,  UPPER_FLOOR,  WEST],  # 11
#    [MIDDLE, UPPER_FLOOR,  WEST]   # 12
]

def main(client, ser):
    while True:
        line = readTempLine(ser)
        values = parseLine(line)
        insertIntoDB(values, client)

def readTempLine(ser):
    # trigger output of the menu in case of a new start
    ser.write('\r'.encode('utf-8'))
    line = readLineFromSerial(ser).strip()
    while not line:
        line = readLineFromSerial(ser).strip()
    if not re.match(r'^(\d+\.\d+;?)+', line):
        print("assuming restart: reconfigurung for interval "+INTERVAL+"s and restarting data collection", flush=True)
        # probably the menu is open -> configure the sensors
        readMenu(ser)
        #configure timeout
        print("setting interval", flush=True)
        ser.write('7\r'.encode('utf-8'))
        readLineFromSerial(ser)
        ser.write((INTERVAL+'\r').encode('utf-8'))
        readMenu(ser)
        # start recording
        print("starting to read", flush=True)
        ser.write('2\r'.encode('utf-8'))
        # wait for all output
        while not re.search(r'OK', line):
            line = readLineFromSerial(ser)
        line = ''
    while not line:
        line = readLineFromSerial(ser).strip()
    return line

def readMenu(ser):
    print("waiting for menu", flush=True)
    line = ''
    while not re.search(r'7: Messinterval', line):
        line = readLineFromSerial(ser)
    readLineFromSerial(ser)
    print("finished waiting for menu", flush=True)

def readLineFromSerial(ser):
    line = ser.read_until('\r'.encode('utf-8')).decode('utf-8')
    print("got line: "+repr(line), flush=True)
    return line

def parseLine(line):
    print("line: "+line, end='', flush=True)
    values = line.split(';')
    values = list(filter(lambda s : len(s) > 0 and s != '\n', values))
    values = list(map(lambda s : s.replace(',','.'), values))
    values = list(map(lambda s : float(s), values))
    return values; 

def insertIntoDB(values, client):
    print("values: "+str(values), flush=True)
    time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    points = list(
        map(
            lambda enum_value: createPoint(enum_value[1], enum_value[0], time),
            list(enumerate(values))
        )
    )
    client.write_points(points)
    print("wrote points to influxdb", flush=True)

def createPoint(value, index, time):
    tags = TAGS[index]
    return  {
                "measurement": "temperature",
                "tags": {
                    POSITION: tags[0],
                    FLOOR: tags[1],
                    DIRECTION: tags[2],
                    "index": str(index)
                },
                "time": time,
                "fields": {
                    "temperature": value
                }
            }



if __name__ == '__main__':
    print("starting", flush=True)
    host = os.getenv("DB_HOST")
    port =  os.getenv("DB_PORT")
    user =  os.getenv("DB_USER")
    password =  os.getenv("DB_PASSWORD")
    dbname =  os.getenv("DB_NAME")
    client = InfluxDBClient(host, port, user, password, dbname)
    print("initialized db-client", flush=True)
    ser = serial.Serial('/dev/ttyUSB0', 19200)
    ser.timeout = 10
    print("initialized serial connection", flush=True)
    main(client, ser)
