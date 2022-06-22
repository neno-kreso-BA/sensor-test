#!/usr/bin/python
# -*- coding: utf-8 -*-
import ST7735
import urllib
from urllib import request,parse
import time 
from datetime import datetime
from bme280 import BME280
import logging
import json
from enviroplus.noise import Noise
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
noise = Noise()


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("test1-Print readings from the BME280 weather sensor and push to API. ")

def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5

REST_API_URL = 'https://api.powerbi.com/beta/ddd66cce-ffe1-4029-967c-5e15ef73127f/datasets/68c21b77-d940-4815-ade3-cf2f56c3895a/rows?key=eFN8uasQB8lLiqo8b95qUC9XXkzF2ilqHFHEa7JOEotKMuQpecfoNXHPcHvSGwv4DLHNS5t%2FqwbJQ5YlnaD9yw%3D%3D'

while True:
    try:

        #cpu_temp
        cpu_temp = get_cpu_temperature()
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        # read and print out humidity and temperature from sensor
        # ensure that timestamp string is formatted properly

        
        now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S%Z')
        humidity = bme280.get_humidity()
        raw_temp = bme280.get_temperature()
        temperature= raw_temp - ((avg_cpu_temp - raw_temp) / factor)

        lux = ltr559.get_lux()     
        amps = noise.get_amplitudes_at_frequency_range([(100, 20000)])
        
        
        logging.info("""Temperature: {:05.2f} *C
        Relative humidity: {:05.2f} %
        Light: {:05.02f} Lux
        Amps: {:05.02f} Amps
        """.format(temperature, humidity,lux,amps))

        # data that we're sending to Power BI REST API

        data = '[{{ "temperature": "{0:05.2f}", "humidity": "{1:05.2f}", "light": "{2:05.2f}", "time": "{3}" }}]'.format(temperature,humidity,lux,now)
        #data = json.dumps(data)
        #data = str(data)
        data = data.encode('utf-8')
        
        

        # make HTTP POST request to Power BI REST API


        req=request.Request(REST_API_URL,data=data)
        response = request.urlopen(req)
        print('POST request to Power BI with data:{0}'.format(data))
        print('Response: HTTP {0} {1}\n'.format(response.getcode(),response.read()))
        
        time.sleep(0.5)
        
    except request.HTTPError as e:
        print('HTTP Error: {0} - {1}'.format(e.code, e.reason))
    except request.URLError as e:
        print('URL Error: {0}'.format(e.reason))
    except Exception as e:
        print('General Exception: {0}'.format(e))
