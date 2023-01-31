#!/usr/bin/python
# *****BatteryMonitor store summary data summary.py*****
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

import sys
from os import rename
import time
from shutil import copy as filecopy
from copy import deepcopy
from ast import literal_eval
from configparser import SafeConfigParser
from config import config
numcells = config['battery']['numcells']
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)


summaryfile = SafeConfigParser()
summaryfile.read(config['files']['summaryfile'])

#logdata =logger.logging.getlogger()
#logdata.setLevel(logger.logging.INFO)
#log.addHandler(logger.logfile)

class Summary:
  """Handles battery summary data"""

  def __init__(self):
    self.currenttime = time.strftime("%Y%m%d%H%M%S ", time.localtime())
    printtime = str(self.currenttime)
    self.logfile = open(config['files']['logfile'],'at',buffering=1)
    self.sampletime = time.time()
    self.prevtime = self.currenttime
    self.summary=self.loadsummary()

#      summary = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/summary','w')
#      pickle.dump(hivolts, summary)
#      pickle.dump(lowvolts, summary)
#      summary.close()
    if str(self.summary['hour']['timestamp'])[0:10] != printtime[0:10]:
      self.summary['hour'] = deepcopy(self.summary['current'])
    if str(self.summary['currentday']['timestamp'])[0:8] != printtime[0:8]:
      self.summary['currentday'] = deepcopy(self.summary['current'])
    if str(self.summary['monthtodate']['timestamp'])[0:6] != printtime[0:6]:
      self.summary['monthtodate'] = deepcopy(self.summary['current'])
    if str(self.summary['yeartodate']['timestamp'])[0:4] != printtime[0:4]:
      self.summary['yeartodate'] = deepcopy(self.summary['current'])

  def loadsummary(self):
    summary = {}
    for section in summaryfile.sections():
      summary[section] = {}
      for key, val in summaryfile.items(section):
        summary[section][key] = literal_eval(val)
#      daysummaryfile = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/daysummary','r')
#      self.daydata = literal_eval(daysummaryfile.read())
#      daysummaryfile.close()
    print(summary['current']['timestamp'])
    return summary


  def update(self, summary, batdata):
    """ Update 'current' section of summary data with 'batdata' and write realtime log """
    self.prevtime = self.currenttime
    self.currenttime = int(time.strftime("%Y%m%d%H%M%S ", time.localtime()))
    self.summary['current']['timestamp'] = str(self.currenttime)
    self.summary['current']['maxvoltages'][numcells] = round(batdata.batvoltsav[numcells],2)
    self.summary['current']['minvoltages'][numcells] = self.summary['current']['maxvoltages'][numcells]
    if batdata.currentav[-3] > -config['battery']['ilowcurrent']:
      self.summary['current']['maxnocharge'][numcells] = self.summary['current']['maxvoltages'][numcells]
    if batdata.currentav[-3] < config['battery']['ilowcurrent']:
      self.summary['current']['minnoload'][numcells] = self.summary['current']['minvoltages'][numcells]
    self.summary['current']['ah'][2] = round(batdata.soc,2)
    self.summary['current']['ah'][0] = self.summary['current']['ah'][2]
    self.summary['current']['ah'][1] = self.summary['current']['ah'][2]
    self.summary['current']['ah'][6] = round(batdata.inahtot,2)  # current from solar etc
    self.summary['current']['dod'][2] = round(batdata.socadj,2)
    self.summary['current']['dod'][0] = self.summary['current']['dod'][2]
    self.summary['current']['dod'][1] = self.summary['current']['dod'][2]
    self.summary['current']['dod'][4] = round(\
    100-100*(self.summary["current"]["dod"][0])/(batdata.batcapresidual),1)

#    self.summary['current']['amps'][1] = round(batdata.currentav[0], 1)
#    self.summary['current']['amps'][0] = self.summary['current']['amps'][1]
#    self.summary['current']['amps'][2] = round(batdata.currentav[1], 1)
    if batdata.ah > 0.0:
      self.summary['current']['ah'][5] = round(batdata.ah,2)
      self.summary['current']['ah'][4] = 0.0
    else:
      self.summary['current']['ah'][4] = round(batdata.ah,2)
      self.summary['current']['ah'][5] = 0.0
    if batdata.pwrbat > 0.0:
      self.summary['current']['power'][1] = round(batdata.pwrbattot,6)
      self.summary['current']['power'][0] = 0.0
    else:
      self.summary['current']['power'][0] = round(batdata.pwrbattot,6)
      self.summary['current']['power'][1] = 0.0
    self.summary['current']['power'][2] = round(batdata.pwrintot,6)
    self.summary['current']['power'][3] = round(self.summary['current']['power'][0] + \
                                     self.summary['current']['power'][2] + \
                                     self.summary['current']['power'][1] ,6 )  # current to loads
    self.summary['current']['batpwr1hrav'][0]=round(batdata.batpwr1hrav,3)
    self.summary['current']['minmaxdemandpwr']=batdata.minmaxdemandpwr
    self.summary['current']['excesssolar'][0]=round(batdata.pwravailable)
    for i in range(len(batdata.chargestates)):
      if batdata.chargestates[i] == b'00':
        self.summary['current']['state'][i] ='Offline'
      elif batdata.chargestates[i] == b'10':
        self.summary['current']['state'][i] ='No Sun'
      elif batdata.chargestates[i] == b'11':
        self.summary['current']['state'][i] ='Bulk'
      elif batdata.chargestates[i] == b'12':
        self.summary['current']['state'][i] ='Absorb'
      elif batdata.chargestates[i] == b'13':
        self.summary['current']['state'][i] ='Float'

    vprint=''
    batdata.vcells=''
    batdata.iall=''
    maxmaxvoltage = 0.0
    minmaxvoltage = 5.0
    for i in range(len(self.summary['current']['maxvoltages'])):
      self.summary['current']['maxvoltages'][i] = round(batdata.voltsav[i+1],3)
      self.summary['current']['minvoltages'][i] = self.summary['current']['maxvoltages'][i]
      if batdata.currentav[-3] > -config['battery']['ilowcurrent']:
        self.summary['current']['maxnocharge'][i] = self.summary['current']['maxvoltages'][i]
      if batdata.currentav[-3] < config['battery']['ilowcurrent']:
        self.summary['current']['minnoload'][i] = self.summary['current']['minvoltages'][i]

    for i in range(numcells):
      maxmaxvoltage = max(maxmaxvoltage, self.summary['current']['maxvoltages'][i])
      minmaxvoltage = min(minmaxvoltage, self.summary['current']['maxvoltages'][i])
      self.summary['current']['baltime'][i]=round(batdata.baltime[i],4)
      batdata.vcells=batdata.vcells+str(round(batdata.voltsav[i+1],3)).ljust(5,'0')+' '

    vprint=vprint + batdata.vcells
    self.summary['current']['deltav'][0] = round(maxmaxvoltage - minmaxvoltage, 3)
    if batdata.currentav[-3] < config['battery']['ilowcurrent']:
      self.summary['current']['deltav'][1] = self.summary['current']['deltav'][0]
    self.summary['current']['deltav'][2] = self.summary['current']['deltav'][0]
    batdata.vbat=str(round(batdata.batvoltsav[numcells],2)).ljust(5,'0')+' '
    vprint = vprint +batdata.vbat
    batdata.vdelta= str(self.summary['current']['deltav'][0]).ljust(5,'0')+' '
    vprint = vprint+batdata.vdelta

    for i in range(batdata.numiins):
      self.summary['current']['ioutmax'][i] = round(batdata.currentav[i],1)
      self.summary['current']['iinmax'][i] = self.summary['current']['ioutmax'][i]
      batdata.iall=batdata.iall+str(round(batdata.currentav[i],1)).ljust(5,'0')+' '
      self.summary['current']['kwoutmax'][i] = round(batdata.currentav[i]*batdata.batvoltsav[numcells]/1000,3)
      self.summary['current']['kwinmax'][i] = self.summary['current']['kwoutmax'][i]
      self.summary['current']['kwhin'][i] = round(batdata.kWhin[i],6)
      self.summary['current']['kwhout'][i] = round(batdata.kWhout[i],6)

    for i in range(len(batdata.tin)): # get temperatures
      self.summary['current']['tmax'][i] = batdata.temp[i]
      self.summary['current']['tmin'][i] = self.summary['current']['tmax'][i]

    vprint = vprint +batdata.iall
    batdata.soctxt=str(round(batdata.soc,2)).ljust(6,'0') +' '
    batdata.socadjtxt=str(round(batdata.socadj,2)).ljust(6,'0') + ' '  #  + '\033[1A'
    sys.stdout.write(eval(config['logging']['data'])+'\n')  #  + '\033[1A'
    self.logfile.write(eval(config['logging']['data'])+'\n')
#    self.publish(data=eval(config['mqtt']['data']))

#    log.info(config['logging']['data'])

  def updatesection(self, summary, section, source):
    """ Update 'summary' section 'section' with data from 'source' """

    section = self.summary[section]
    source = self.summary[source]
    section['deltav'][1] = max(section['deltav'][1], source['deltav'][1])
    section['deltav'][2] = max(section['deltav'][2], source['deltav'][2])
    section['deltav'][0] = min(section['deltav'][0], source['deltav'][0])
    section['ah'][2] = max(section['ah'][2], source['ah'][2])
    section['ah'][0] = min(section['ah'][0], source['ah'][0])
    section['ah'][1] = (section['ah'][1]*section['ah'][3] + source['ah'][1])
    section['ah'][4] = round(section['ah'][4]+source['ah'][4], 2)
    section['ah'][5] = round(section['ah'][5]+source['ah'][5], 2)
    section['ah'][6] = round(section['ah'][6]+source['ah'][6], 2)
    section['power'][0] = round(section['power'][0]+source['power'][0], 6)
    section['power'][1] = round(section['power'][1]+source['power'][1], 6)
    section['power'][2] = round(section['power'][2]+source['power'][2], 6)
    section['power'][3] = round(section['power'][3]+source['power'][3], 6)
    section['dod'][2] = max(section['dod'][2], source['dod'][2])
    section['dod'][0] = min(section['dod'][0], source['dod'][0])
    section['dod'][1] = (section['dod'][1]*section['ah'][3] + source['dod'][1])
    section['ah'][3] += 1
    section['ah'][1] = round(section['ah'][1]/section['ah'][3], 6)
    section['dod'][1] = round(section['dod'][1]/section['ah'][3], 6)
    section['dod'][3] = max(section['dod'][3], source['dod'][3])
#    section['amps'][1] = max(section['amps'][1], source['amps'][1])
#    section['amps'][0] = min(section['amps'][0], source['amps'][0])
#    section['amps'][2] = min(section['amps'][2], source['amps'][2])
    for i in range(len(config['CurrentInputs'])):
      section['ioutmax'][i] = max(section['ioutmax'][i], source['ioutmax'][i])
      section['iinmax'][i] = min(section['iinmax'][i], source['iinmax'][i])
      section['kwoutmax'][i] = max(section['kwoutmax'][i], source['kwoutmax'][i])
      section['kwinmax'][i] = min(section['kwinmax'][i], source['kwinmax'][i])
      section['kwhin'][i] = round(source['kwhin'][i]+section['kwhin'][i], 5)
      section['kwhout'][i] = round(source['kwhout'][i]+section['kwhout'][i], 5)
    for i in range(len(self.summary['current']['maxvoltages'])):
      section['maxvoltages'][i] = max(section['maxvoltages'][i], source['maxvoltages'][i])
      section['minvoltages'][i] = min(section['minvoltages'][i], source['minvoltages'][i])
      section['maxnocharge'][i] = max(section['maxnocharge'][i], source['maxnocharge'][i])
      section['minnoload'][i] = min(section['minnoload'][i], source['minnoload'][i])
    for i in range(numcells):
      section['baltime'][i] = round(section['baltime'][i]+source['baltime'][i],4)
    for i in range(len(config['TemperatureInputs'])):
      section['tmax'][i] = max(section['tmax'][i], source['tmax'][i])
      section['tmin'][i] = min(section['tmin'][i], source['tmin'][i])
    section['timestamp'] = self.summary['current']['timestamp']

  def writesummary(self):
    """ Write summary file """

    for section in summaryfile.sections():
      for option in summaryfile.options(section):
        summaryfile.set(section, option, str(self.summary[section][option]))
    of = open(config['files']['summaryfile'],'w')
    summaryfile.write(of)
    of.close()

#  def writehour(self, data):
#    hoursummaryfile=open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/hoursummary','a')
#    hoursummaryfile.write(data)
#    hoursummaryfile.close()
#    logsummary.set('alltime', 'maxvoltages') = round(max(literal_eval(logsummary.get('currentday','maxvoltages')),literal_eval(logsummary.get(),2)
#    logsummary.set('alltime', 'minvoltages') = round(min(literal_eval(logsummary.get('currentday','minvoltages')),batdata.batvoltsav[8]),2)
#    logsummary.set('alltime', 'ah') = round(max(literal_eval(logsummary.get('currentday','ah'))[1], batdata.soc/1000),2)
#    logsummary.set('alltime', 'ah') = round(min(literal_eval(logsummary.get('currentday','ah'))[0], batdata.soc/1000),2)
#    logsummary.set('alltime', 'current') = round(max(literal_eval(logsummary.get('alltime','current'))[1], batdata.currentav[-3]/1000),2)
#    logsummary.set('alltime', 'current') = round(min(literal_eval(logsummary.get('alltime','current'))[0], batdata.currentav[-3]/1000),2)


  def writeperiod(self, file, data):
    """ Append 'data' to 'file' for previous period """
    periodfile=open(config['files'][file],'a')
    writestr=''
    y = summaryfile.items(data)
    for i in y:
      writestr = writestr + str(i) +"\n"
    writestr = writestr + "\n"
    periodfile.write(writestr)
    periodfile.close()

  def starthour(self, summary):
    """ Start new hour """
    self.writeperiod('hoursummaryfile', 'hour')
    self.summary['hour']['ah'][3] = 0 # zero # of samples for av
    self.summary['hour'] = deepcopy(self.summary['current'])

  def startday(self, summary):
    """ Start new Day """

    self.writeperiod('daysummaryfile', 'currentday')
    self.summary['prevday'] = deepcopy(self.summary['currentday'])
    self.summary['currentday']['ah'][3] = 0 # zero number of samples for av
    self.summary['current']['dod'][3] += 1
    self.summary['currentday'] = deepcopy(self.summary['current'])

  def startmonth(self, summary):
    """ Start new month """

    self.writeperiod('monthsummaryfile', 'monthtodate')
    self.summary['monthtodate']['ah'][3] = 0  # zero number of samples for av
    self.summary['monthtodate'] = deepcopy(self.summary['current'])
    filecopy(config['files']['summaryfile'],config['files']['summaryfile']+ str(self.currenttime)[0:8])

  def startyear(self, summary):
    """ Start new year """

    self.writeperiod('yearsummaryfile', 'yeartodate')
    self.summary['yeartodate']['ah'][3] = 0  # zero number of samples for av
    self.summary['yeartodate'] = deepcopy(self.summary['current'])
    self.logfile.close()
    rename(config['files']['logfile'],config['files']['logfile']+str(int(str(self.currenttime)[0:4])-1))
    self.logfile = open(config['files']['logfile'],'a')

  def close(self):
    """ Close logging file ready for exit """

    self.logfile.close()
