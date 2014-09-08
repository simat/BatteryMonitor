#!/usr/bin/python
import sys
#import smbus
#from Adafruit_I2C import Adafruit_I2C
import summary
from config import config
numcells = config['battery']['numcells']
from getdata import Readings
batdata = Readings()
logsummary= summary.Summary()
summary = logsummary.summary

def deamon(soc=0):
  prevtime = logsummary.currenttime
  prevbatvoltage = batdata.batvoltsav[numcells]
  soc = soc * 1000
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
        if batdata.batvoltsav[numcells] >= 27.6 and prevbatvoltage < 27.6:
          batdata.soc = 0.0
        else:
          batdata.soc = batdata.soc + batdata.batcurrentav*(batdata.sampletime-batdata.oldsampletime)/3600
      prevbatvoltage = batdata.batvoltsav[numcells]
      logsummary.update(summary, batdata)
      if logsummary.currenttime[4] <> logsummary.prevtime[4]:  # new minute
        logsummary.updatesection(summary, 'hour', 'current')
        logsummary.updatesection(summary, 'alltime','current')
        logsummary.updatesection(summary, 'currentday','current')
        logsummary.updatesection(summary, 'monthtodate', 'current')
        logsummary.updatesection(summary, 'yeartodate', 'current')
        logsummary.writesummary()

      if logsummary.currenttime[3] <> logsummary.prevtime[3]:  # new hour
        logsummary.starthour(summary)

      if logsummary.currenttime[3] < logsummary.prevtime[3]: # newday
        logsummary.startday(summary)

      if logsummary.currenttime[1] != logsummary.prevtime[1]: # new month
        logsummary.startmonth(summary)

      if logsummary.currenttime[1] != logsummary.prevtime[1]: # new year
        logsummary.startyear(summary)

    except KeyboardInterrupt:
      sys.stdout.write('\n')
      logsummary.close()
      break

if __name__ == "__main__":
  print (sys.argv)
  deamon(float(sys.argv[1]))
