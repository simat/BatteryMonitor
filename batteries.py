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
#import Adafruit_ADS1x15
import time
from shutil import copy as filecopy
from config import loadconfig, config
from configparser import SafeConfigParser
numcells = config['battery']['numcells']
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)
from demandmanager import solaravailable
from getdata import Readings
from alarms import Alarms
maxtries=3 # number of error retries befor abort
#exec(config['files']['alarms'])  # import alarm code
#import Adafruit_BBIO.GPIO as GPIO

def initmain(soc):
  """ initialise main loop, soc is SOC to start battery DOD to"""
  summary = logsummary.summary
  printtime = int(time.strftime("%Y%m%d%H%M%S ", time.localtime()))
  print (int(summary['current']['timestamp']),printtime)
  while printtime < int(summary['current']['timestamp']):
    print(printtime,summary['current']['timestamp'])
    print ("Error: Current time before last sample time")
    time.sleep(30)
    printtime = int(time.strftime("%Y%m%d%H%M%S", time.localtime()))

  print (printtime)
  filecopy(config['files']['summaryfile'],config['files']['summaryfile']+"R" + str(int(printtime)))
  if soc > config['battery']['capacity']:
    print ("Battery DOD must be less than Battery Capacity")

  else:
    if soc < 0:
       batdata.soc = summary['current']['ah'][0]
       batdata.socadj = summary['current']['dod'][0]
    else:
      batdata.soc = soc
      batdata.socadj = soc
      summary['current']['dod'][3] = 0
    summary['current']['dod'][3] = -100 # flag don't adjust leakage current
    prevtime = logsummary.currenttime
#    logsummary.startday(summary)
#    logsummary.starthour(summary)

def mainloop():
  """ Main loop, gets battery data, gets summary.py to do logging"""
  prevbatvoltage = batdata.batvoltsav[numcells]

  for i in range(config['sampling']['samplesav']):
#          printvoltage = ''
#          for i in range(numcells+1):
#            printvoltage = printvoltage + str(round(batdata.batvolts[i],3)).ljust(5,'0') + ' '
#         print (printvoltage)
    batdata.getraw()

#          if batdata.batvoltsav[numcells] >= 55.2 and prevbatvoltage < 55.2:  # reset SOC counter?
#          print batdata.socadj/(float(summary['current']['dod'][3])*24.0)
  if batdata.batvoltsav[numcells] < config['battery']['vreset'] \
  and prevbatvoltage >= config['battery']['vreset'] \
  and summary['current']['dod'][3] != 0 \
  and -batdata.currentav[-3] < config['battery']['ireset']:  # reset SOC counter?

    if summary['current']['dod'][3] <= 0 :
      socerr=0
    else:
      socerr=batdata.socadj/(float(summary['current']['dod'][3])*24.0)
      socerr=max(socerr,-0.01)
      socerr=min(socerr,0.01)
    config['battery']['ahloss']=config['battery']['ahloss']-socerr/2
    batconfigdata=SafeConfigParser()
    batconfigdata.read('battery.cfg')
    batconfigdata.set('battery','ahloss',str(config['battery']['ahloss']))
    with open('battery.cfg', 'w') as batconfig:
      batconfigdata.write(batconfig)
    batconfig.closed

    batdata.soc = config['battery']['socreset']
    batdata.socadj = batdata.soc
    summary['current']['dod'][3] = 0
  else:
    batdata.soc = batdata.soc + batdata.batah
    batdata.socadj = batdata.socadj +batdata.batahadj

  batdata.ah = batdata.ah + batdata.batah
  batdata.inahtot = batdata.inahtot + batdata.inah
  batdata.pwrbattot = batdata.pwrbattot + batdata.pwrbat
  batdata.pwrintot = batdata.pwrintot + batdata.pwrin
# check alarms
  alarms.scanalarms(batdata)
# update summaries
  logsummary.update(summary, batdata)
  currenttime=str(logsummary.currenttime)
  prevtime=str(logsummary.prevtime)
  if currenttime[10:12] != prevtime[10:12]:  # new minute
    loadconfig()
    batdata.pwravailable,batdata.minmaxdemandpwr=solaravailable(batdata)
    logsummary.updatesection(summary, 'hour', 'current')
    logsummary.updatesection(summary, 'alltime','current')
    logsummary.updatesection(summary, 'currentday','current')
    logsummary.updatesection(summary, 'monthtodate', 'current')
    logsummary.updatesection(summary, 'yeartodate', 'current')
    logsummary.writesummary()
    batdata.ah = 0.0
    batdata.ahadj = 0.0
    batdata.inahtot = 0.0
    batdata.pwrbattot = 0.0
    batdata.pwrintot = 0.0
    for i in range(batdata.numiins):
      batdata.kWhin[i] = 0.0
      batdata.kWhout[i] = 0.0
    for i in range(numcells):
      batdata.baltime[i]=0

  if currenttime[8:10] != prevtime[8:10]:  # new hour
    logsummary.starthour(summary)

  if currenttime[6:8] != prevtime[6:8]: # newday
    logsummary.startday(summary)

  if currenttime[4:6] != prevtime[4:6]: # new month
    logsummary.startmonth(summary)

  if currenttime[0:4] != prevtime[0:4]: # new year
    logsummary.startyear(summary)

import summary
logsummary=summary.Summary()
batdata = Readings()  # initialise batdata
alarms = Alarms(batdata,summary) # initialise alarms
def deamon(soc=-1):
  """Battery Management deamon to run in background"""

  numtries=0
  while True:
    try:
      initmain(soc)
      while True:
        mainloop()
        numtries=0
    except KeyboardInterrupt:
      numtries=maxtries
      sys.stdout.write('\n')
      logsummary.close()
      raise
  #    sys.exit(9)
    except Exception as err:
      log.critical(err)
      numtries+=1
      soc=-1
      if numtries==maxtries:
        logsummary.close()
        raise


if __name__ == "__main__":
  print (sys.argv)
  if len(sys.argv) > 1:
    deamon(float(sys.argv[1]))
  else:
    deamon()
