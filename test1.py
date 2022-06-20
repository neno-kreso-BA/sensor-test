#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import time
from datetime import datetime
from bme280 import BME280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# REST API endpoint, given to you when you create an API streaming dataset
# Will be of the format: https://api.powerbi.com/beta/<tenant id>/datasets/< dataset id>/rows?key=<key id>

REST_API_URL = ' https://api.powerbi.com/beta/ddd66cce-ffe1-4029-967c-5e15ef73127f/datasets/68c21b77-d940-4815-ade3-cf2f56c3895a/rows?key=eFN8uasQB8lLiqo8b95qUC9XXkzF2ilqHFHEa7JOEotKMuQpecfoNXHPcHvSGwv4DLHNS5t%2FqwbJQ5YlnaD9yw%3D%3D '

while True:
    try:

        # read and print out humidity and temperature from sensor

        humidity = bme280.get_humidity()
        temp = bme280.get_temperature()
        print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temp,humidity))

        # ensure that timestamp string is formatted properly

        now = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S%Z')

        # data that we're sending to Power BI REST API

        data = '[{{ "temperature": "{1:0.1f}", "humidity": "{2:0.1f}", "timestamp": "{0}" }}]'.format(now,temp, humidity)

        # make HTTP POST request to Power BI REST API

        req = urllib2.Request(REST_API_URL, data)
        response = urllib2.urlopen(req)
        print('POST request to Power BI with data:{0}'.format(data))
        print('Response: HTTP {0} {1}\n'.format(response.getcode(),response.read()))

        time.sleep(1)
    except urllib2.HTTPError, e:
        print('HTTP Error: {0} - {1}'.format(e.code, e.reason))
    except urllib2.URLError, e:
        print('URL Error: {0}'.format(e.reason))
    except Exception, e:
        print('General Exception: {0}'.format(e))
