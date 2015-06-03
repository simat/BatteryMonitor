# *****BatteryMonitor calibration file calibrate.py*****
# Copyright (C) 2014 Simon Richard Matthews
# Project loaction https://github.com/simat/BatteryMonitor
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


#!/usr/bin/python
import sys
#import smbus
#from Adafruit_I2C import Adafruit_I2C
from config import config
numcells = config['battery']['numcells']
from getdata import Readings
batdata = Readings()

def calibrate():

  while True:
    try:
      for i in range(config['sampling']['samplesav']):
        batdata.getraw()
      printvoltage = ''
      for i in range(numcells+1):
        printvoltage = printvoltage + str(round(batdata.uncalvolts[i],3)).ljust(5,'0') + ' '
      printvoltage = printvoltage + '\n'
      for i in range(1, numcells+1):
        printvoltage = printvoltage + str(round(batdata.uncalvolts[i]-batdata.uncalvolts[i-1],3)).ljust(5,'0') + ' '
      printvoltage = printvoltage +'\n'

      for i in range(numcells+1):
        printvoltage = printvoltage + str(round(batdata.batvolts[i],3)).ljust(5,'0') + ' '
      printvoltage = printvoltage + '\n'
      for i in range(1, numcells+1):
        printvoltage = printvoltage + str(round(batdata.batvolts[i]-batdata.batvolts[i-1],3)).ljust(5,'0') + ' '
      printvoltage = printvoltage +'\n'
      for i in range(1, numcells+1):
        printvoltage = printvoltage + str(round(batdata.batvolts[i]-batdata.batvolts[i-1]+batdata.calvolts[i],3)).ljust(5,'0') + ' '
      printvoltage = printvoltage +'\n'
      print (printvoltage)


    except KeyboardInterrupt:
      break

if __name__ == "__main__":
  calibrate()
