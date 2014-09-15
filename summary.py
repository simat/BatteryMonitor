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
import time
from copy import deepcopy
from ast import literal_eval
from ConfigParser import SafeConfigParser
from config import config
numcells = config['battery']['numcells']


class Summary:
  """Handles battery summary data""" 

#  hivolts = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#  lowvolts = [ 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
#  summary = {}
#    self.summary['hour']['minvoltages'] = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 30.0]
#    self.summary['hour']['maxvoltages'] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#    self.summary['hour']['ah'] = [100000.0, 0.0]
#    self.summary['hour']['current'] = [1000.0, -100.0]


  def __init__(self):
    self.currenttime = time.localtime()
    printtime = time.strftime("%Y%m%d%H%M%S ", self.currenttime)
    self.logfile = open(config['files']['logfile'],'a')
    self.sampletime = time.time()
    self.prevtime = time.localtime()
    try:
      self.summaryfile = SafeConfigParser()
      self.summaryfile.read('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/summary')
      self.summary = {}
      for section in self.summaryfile.sections():
        self.summary[section] = {}
        for key, val in self.summaryfile.items(section):
          self.summary[section][key] = literal_eval(val)
#      daysummaryfile = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/daysummary','r')
#      self.daydata = literal_eval(daysummaryfile.read())
#      daysummaryfile.close()
    except IOError:
      pass
#      summary = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/summary','w')
#      pickle.dump(hivolts, summary)
#      pickle.dump(lowvolts, summary)
#      summary.close()
    if self.summary['hour']['timestamp'][0:10] != printtime[0:10]:
      self.summary['hour'] = deepcopy(self.summary['current'])
    if self.summary['currentday']['timestamp'][0:8] != printtime[0:8]:
      self.summary['currentday'] = deepcopy(self.summary['current'])
    if self.summary['monthtodate']['timestamp'][0:6] != printtime[0:6]:
      self.summary['monthtodate'] = deepcopy(self.summary['current'])
    if self.summary['yeartodate']['timestamp'][0:4] != printtime[0:4]:
      self.summary['yeartodate'] = deepcopy(self.summary['current'])



  def update(self, summary, batdata):
    summary['current']['maxvoltages'][numcells] = round(batdata.batvoltsav[numcells],2)
    summary['current']['minvoltages'][numcells] = summary['current']['maxvoltages'][numcells]
    if batdata.batcurrentav < 10000:
      summary['current']['minnoload'][numcells] = summary['current']['minvoltages'][numcells]
    summary['current']['minvoltages'][numcells] = summary['current']['maxvoltages'][numcells]
    summary['current']['ah'][1] = round(batdata.soc/1000,2)
    summary['current']['ah'][0] = summary['current']['ah'][1]
    summary['current']['amps'][1] = round(batdata.batcurrentav/1000, 1)
    summary['current']['amps'][0] = summary['current']['amps'][1]
    vprint=''
    maxmaxvoltage = 0.0
    minmaxvoltage = 5.0    
    for i in range(numcells):
      summary['current']['maxvoltages'][i] = round(batdata.deltav[i+1],3)
      maxmaxvoltage = max(maxmaxvoltage, summary['current']['maxvoltages'][i])
      minmaxvoltage = min(minmaxvoltage, summary['current']['maxvoltages'][i])
      summary['current']['minvoltages'][i] = summary['current']['maxvoltages'][i]
      if batdata.batcurrentav < 10000:
        summary['current']['minnoload'][i] = summary['current']['minvoltages'][i]     
      vprint=vprint + str(round(batdata.deltav[i+1],3)).ljust(5,'0') + ' '
    summary['current']['deltav'][0] = round(maxmaxvoltage - minmaxvoltage, 3)
    if batdata.batcurrentav < 10000:
      summary['current']['deltav'][1] = summary['current']['deltav'][0]
    summary['current']['deltav'][2] = summary['current']['deltav'][0]
    vprint = vprint + str(round(batdata.batvoltsav[numcells],2)).ljust(5,'0') + ' '
    vprint = vprint + str(summary['current']['deltav'][0]) + ' '
    logdata = vprint + str(round(batdata.batcurrentav/1000,1)) + ' ' + str(round(batdata.soc/1000,2)).ljust(5,'0') + '\n'  #  + '\033[1A'    
    sys.stdout.write(logdata)  #  + '\033[1A'
    self.prevtime = self.currenttime
    self.currenttime = time.localtime()
    printtime = time.strftime("%Y%m%d%H%M%S ", self.currenttime)
    summary['current']['timestamp'] = "'" + printtime + "'"
    currentdata = printtime + logdata

#      currentdata = currentdata + '               '
#      for i in range(numcells):
#        currentdata = currentdata + str(round(batdata.uncalvolts[i+1]-batdata.uncalvolts[i],3)) + ' ' 
#      currentdata = currentdata + '\n'
    self.logfile.write(currentdata)

  def updatesection(self, summary, section, source):
    summary[section]['deltav'][1] = max(summary[section]['deltav'][1], summary[source]['deltav'][1])
    summary[section]['deltav'][2] = max(summary[section]['deltav'][2], summary[source]['deltav'][2])
    summary[section]['deltav'][0] = min(summary[section]['deltav'][0], summary[source]['deltav'][0])
    summary[section]['ah'][1] = max(summary[section]['ah'][1], summary[source]['ah'][1])
    summary[section]['ah'][0] = min(summary[section]['ah'][0], summary[source]['ah'][0])
    summary[section]['amps'][1] = max(summary[section]['amps'][1], summary[source]['amps'][1])
    summary[section]['amps'][0] = min(summary[section]['amps'][0], summary[source]['amps'][0])     
    for i in range(numcells+1):
      summary[section]['maxvoltages'][i] = max(summary[section]['maxvoltages'][i], summary[source]['maxvoltages'][i])
      summary[section]['minvoltages'][i] = min(summary[section]['minvoltages'][i], summary[source]['minvoltages'][i])
      summary[section]['minnoload'][i] = min(summary[section]['minnoload'][i], summary[source]['minnoload'][i])
    summary[section]['timestamp'] = summary['current']['timestamp']

  def writesummary(self):
    for section in self.summaryfile.sections():
      for option in self.summaryfile.options(section):
        self.summaryfile.set(section, option, str(self.summary[section][option]))
    of = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/summary','w')
    self.summaryfile.write(of)
    of.close()

  def writehour(self, data):
    hoursummaryfile=open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/hoursummary','a')
    hoursummaryfile.write(data)
    hoursummaryfile.close()
#    logsummary.set('alltime', 'maxvoltages') = round(max(literal_eval(logsummary.get('currentday','maxvoltages')),literal_eval(logsummary.get(),2)
#    logsummary.set('alltime', 'minvoltages') = round(min(literal_eval(logsummary.get('currentday','minvoltages')),batdata.batvoltsav[8]),2)
#    logsummary.set('alltime', 'ah') = round(max(literal_eval(logsummary.get('currentday','ah'))[1], batdata.soc/1000),2)
#    logsummary.set('alltime', 'ah') = round(min(literal_eval(logsummary.get('currentday','ah'))[0], batdata.soc/1000),2)
#    logsummary.set('alltime', 'current') = round(max(literal_eval(logsummary.get('alltime','current'))[1], batdata.batcurrentav/1000),2)
#    logsummary.set('alltime', 'current') = round(min(literal_eval(logsummary.get('alltime','current'))[0], batdata.batcurrentav/1000),2)


  def writeperiod(self, file, data):
    periodfile=open(config['files'][file],'a')
    writestr=''
    y = self.summaryfile.items(data)
    for i in y:
      writestr = writestr + str(i) +"\n"
    writestr = writestr + "\n"
    periodfile.write(writestr)
    periodfile.close()
 
  def starthour(self, summary):
    summary['hour'] = deepcopy(summary['current'])

  def startday(self, summary):
    self.writeperiod('daysummaryfile', 'currentday')
    summary['prevday'] = deepcopy(summary['currentday'])
    summary['currentday'] = deepcopy(summary['current'])

  def startmonth(self, summary):
    self.writeperiod('monthsummaryfile', 'monthtodate')
    summary['monthtodate'] = deepcopy(summary['current'])

  def startyear(self, summary):
    self.writeperiod('yearsummaryfile', 'yeartodate')
    summary['yeartodate'] = deepcopy(summary['current'])

  def close(self):
    logsummary.logfile.close()


