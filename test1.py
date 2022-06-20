#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
from urllib import request,parse
import time 
from datetime import datetime
from bme280 import BME280
import logging
import json

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("test1-Print readings from the BME280 weather sensor and push to API. ")

REST_API_URL = ' https://api.powerbi.com/beta/ddd66cce-ffe1-4029-967c-5e15ef73127f/datasets/68c21b77-d940-4815-ade3-cf2f56c3895a/rows?key=eFN8uasQB8lLiqo8b95qUC9XXkzF2ilqHFHEa7JOEotKMuQpecfoNXHPcHvSGwv4DLHNS5t%2FqwbJQ5YlnaD9yw%3D%3D '

while True:
    try:

        # read and print out humidity and temperature from sensor
        # ensure that timestamp string is formatted properly

        now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S%Z')
        humidity = bme280.get_humidity()
        temperature = bme280.get_temperature()

        logging.info("""Temperature: {:05.2f} *C
        Relative humidity: {:05.2f} %
        """.format(temperature, humidity))

        # data that we're sending to Power BI REST API

        data = '[{{ "temperature": "{0:f}", "humidity": "{0:f}", "timestamp": "{0}" }}]'.format(temperature,humidity,now)
        data = json.dumps(data)
        data = str(data)
        data = data.encode('utf-8')
        
        

        # make HTTP POST request to Power BI REST API


        req=request.Request(REST_API_URL,data=data)
        response = request.urlopen(req)
        print('POST request to Power BI with data:{0}'.format(data))
        print('Response: HTTP {0} {1}\n'.format(response.getcode(),response.read()))
        
        time.sleep(1)
        
    except request.HTTPError as e:
        print('HTTP Error: {0} - {1}'.format(e.code, e.reason))
    except request.URLError as e:
        print('URL Error: {0}'.format(e.reason))
    # except Exception as e:
        # print('General Exception: {0}'.format(e))
