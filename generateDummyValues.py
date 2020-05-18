#!/usr/bin/env python3

import random
import time

values = [15,20,25]*4 # default 20 degrees, 3 sensors in 4 locations

while True: 
    values = list(map(lambda x: x+random.uniform(-0.5,0.5), values))
    for value in values:
#        print('{:0.2f}'.format(value)+';', end='')
        print('{:0.2f}'.format(value).replace('.',',')+';', end='')
    print(flush=True)
    time.sleep(5)

