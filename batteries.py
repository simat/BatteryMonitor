# *****BatteryMonitor main file batteries.py*****
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
import Adafruit_BBIO.GPIO as GPIO
# Initialise and compile alarms
for i in config['alarms']:
  exec(config['alarms'][i][0])
  config['alarms'][i][2] = compile(config['alarms'][i][2], '<string>', 'exec') 
  config['alarms'][i][4] = compile(config['alarms'][i][4], '<string>', 'exec') 


def deamon(soc=0):
  """ Main loop, gets battery data, gets summary.py to do logging"""
  import summary
  logsummary = summary.Summary()
  summary = logsummary.summary
  prevtime = logsummary.currenttime
  prevbatvoltage = batdata.batvoltsav[numcells]
  batdata.soc = soc
#  logsummary.startday(summary)
#  logsummary.starthour(summary)


  while True:
    try:
      for i in range(config['sampling']['samplesav']):
#        printvoltage = ''
#        for i in range(numcells+1):
#          printvoltage = printvoltage + str(round(batdata.batvolts[i],3)).ljust(5,'0') + ' '
#        print (printvoltage)
        batdata.getraw()
        
        if batdata.batvoltsav[numcells] >= 27.6 and prevbatvoltage < 27.6:  # reset SOC counter?
          batdata.soc = 0.0
        else:
          batdata.soc = batdata.soc + batdata.batah
        batdata.ah = batdata.ah + batdata.batah
      prevbatvoltage = batdata.batvoltsav[numcells]
# check alarms
      minvolts = 5.0
      maxvolts = 0.0
      for i in range(1,numcells):
        minvolts = min(batdata.deltav[i],minvolts)
        maxvolts = max(batdata.deltav[i],maxvolts)
      for i in config['alarms']:
        if config['alarms'][i][1] > minvolts:
          exec(config['alarms'][i][2])
        if config['alarms'][i][3] < maxvolts:
          exec(config['alarms'][i][4])
# update summaries
      logsummary.update(summary, batdata)
      if logsummary.currenttime[4] <> logsummary.prevtime[4]:  # new minute
        logsummary.updatesection(summary, 'hour', 'current')
        logsummary.updatesection(summary, 'alltime','current')
        logsummary.updatesection(summary, 'currentday','current')
        logsummary.updatesection(summary, 'monthtodate', 'current')
        logsummary.updatesection(summary, 'yeartodate', 'current')
        logsummary.writesummary()
        batdata.ah = 0.0

      if logsummary.currenttime[3] <> logsummary.prevtime[3]:  # new hour
        logsummary.starthour(summary)

      if logsummary.currenttime[3] < logsummary.prevtime[3]: # newday
        logsummary.startday(summary)

      if logsummary.currenttime[1] != logsummary.prevtime[1]: # new month
        logsummary.startmonth(summary)

      if logsummary.currenttime[0] != logsummary.prevtime[0]: # new year
        logsummary.startyear(summary)

    except KeyboardInterrupt:
      sys.stdout.write('\n')
      logsummary.close()
      break

if __name__ == "__main__":
  print (sys.argv)
  deamon(float(sys.argv[1]))
