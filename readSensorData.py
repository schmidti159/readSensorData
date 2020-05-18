#!/usr/bin/env python3

import sys
import os
from datetime import datetime
from influxdb import InfluxDBClient
from dotenv import load_dotenv
load_dotenv(verbose=True)

#constants
POSITION = "Position"
OUTER = "Außen"
MIDDLE = "Mitte"
INNER = "Innen"
FLOOR = "Etage"
UPPER_FLOOR = "OG"
GROUND_FLOOR = "EG"
DIRECTION = "Ausrichtung"
EAST = "Ost"
WEST = "West"

#tag configuration. Depends on the order of the values in the input
tags = [
    [INNER,  GROUND_FLOOR, EAST], # 01
    [MIDDLE, GROUND_FLOOR, EAST], # 02
    [OUTER,  GROUND_FLOOR, EAST], # 03
    [INNER,  GROUND_FLOOR, WEST], # 04
    [MIDDLE, GROUND_FLOOR, WEST], # 05
    [OUTER,  GROUND_FLOOR, WEST], # 06
    [INNER,  UPPER_FLOOR,  EAST], # 07
    [MIDDLE, UPPER_FLOOR,  EAST], # 08
    [OUTER,  UPPER_FLOOR,  EAST], # 09
    [INNER,  UPPER_FLOOR,  WEST], # 10
    [MIDDLE, UPPER_FLOOR,  WEST], # 11
    [OUTER,  UPPER_FLOOR,  WEST]  # 12
]

def main(client):
    while True:
        line = sys.stdin.readline()
        values = parseLine(line)
        insertIntoDB(values, client)

def parseLine(line):
    print("line: "+line, end='')
    values = line.split(';')
    values = list(filter(lambda s : len(s) > 0 and s != '\n', values))
    values = list(map(lambda s : s.replace(',','.'), values))
    values = list(map(lambda s : float(s), values))
    return values; 

def insertIntoDB(values, client):
    print("values: "+str(values))
    time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    points = list(
        map(
            lambda enum_value: createPoint(enum_value[1], tags[enum_value[0]], time),
            list(enumerate(values))
        )
    )
    client.write_points(points)
    print("wrote points to influxdb")

def createPoint(value, tags, time):
    return  {
                "measurement": "temperature",
                "tags": {
                    POSITION: tags[0],
                    FLOOR: tags[1],
                    DIRECTION: tags[2]
                },
                "time": time,
                "fields": {
                    "temperature": value
                }
            }



if __name__ == '__main__':
    host = os.getenv("DB_HOST")
    port =  os.getenv("DB_PORT")
    user =  os.getenv("DB_USER")
    password =  os.getenv("DB_PASSWORD")
    dbname =  os.getenv("DB_NAME")
    client = InfluxDBClient(host, port, user, password, dbname)
    main(client)
