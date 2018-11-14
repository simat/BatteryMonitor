
#!/usr/bin/python
# *****BatteryMonitor Getdata from battery cells getdata.py*****
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

#from test import config
import re
from config import config
numcells = config['battery']['numcells']
import time
#from x import Raw

class Readings:
  """ get and manipulates readings from the real world"""

  for i in config['Interfaces']:
    interface=re.match(r'\w*',config['Interfaces'][i]).group()
    snstring=re.compile(r'[(].*[^)]')
    sn=snstring.search(config['Interfaces'][i])
    if sn!=None:
      sn=sn.group()

    exec("import " + interface)
    print (i)
    if sn==None:
      exec(i +'='+interface+'.Rawdat()')
    else:
      exec(i +'='+interface+".Rawdat('"+str(sn[1:])+"')")

  measured = config['calibrate']['measured']
  displayed = config['calibrate']['displayed']

  ratio = [ 1.0 for i in range(numcells+1)]
  for i in range(1, numcells+1):
    ratio[i] = measured[i]/displayed[i]
  calvolts = [ 0.0 for i in range(numcells+1)]

#  calvolts = [measureddelta[i] - displayeddelta[i] for i in range(numcells+1)]
  deltav = [ 3.25 for i in range(numcells+1)]
  deltav[0] = 0.0
  rawvolts = [ 0.0 for i in range(numcells+1)]
  batvolts = [ i*3.25 for i in range(numcells+1)]
  uncalvolts = [ i*3.25 for i in range(numcells+1)]
  batvoltsav = [ i*3.25 for i in range(numcells+1)]
  balflg = [ 0.0 for i in range(numcells)]
  baltime = [ 0.0 for i in range(numcells)]
  temp = [ 0.0 for i in range(len(config['TemperatureInputs']))]
  numiins = len(config['CurrentInputs'])
  current = [ 0.0 for i in range(numiins)]
  currentav = [ 0.0 for i in range(numiins)]
  kWhin = [ 0.0 for i in range(numiins)]
  kWhout = [ 0.0 for i in range(numiins)]
  chargestates = [ b'00' for i in range(len(config['Status']))]

#  rawcurrent = 0.0
#  batcurrent = 0.0
#  batcurrentav = 0.0
#  rawincurrent = 0.0
#  incurrent = 0.0
#  incurrentav = 0.0
  soc = 0.0
  socadj = 0.0
  batah = 0.0
  batahadj = 0.0
  inah = 0.0
  inahtot = 0.0
  ah = 0.0

  mincellv=100.0
  maxcellv=0.0
  lastmaxv = 0.0 # previous sample maximum cell voltage
  lastminv = 100.0 # previous sample minimum cell voltage
  pwrbat = 0.0 # battery power units kW
  pwrbattot = 0.0  # total battery power units kWh
  pwrin = 0.0  # gross power in units kW
  pwrintot = 0.0 # total gross power in units kWh
  iall=""
  vdelta=""
  vcells=""
  soctxt=""
  socadjtxt=""
  sampleshr=3600/config['sampling']['sampletime'] # numder of sample / hour
  batpwr1hrav = 0.0

  def __init__(self):
    self.vin = []
    for i in sorted(config['VoltageInputs']):
      self.vin = self.vin + [config['VoltageInputs'][i]]
#      self.vin = self.vin + [compile('self.'+config['VoltageInputs'][i], '<string>', 'eval')]
    self.iin = []
    for i in sorted(config['CurrentInputs']):
      self.iin = self.iin + [config['CurrentInputs'][i]]
#      self.iin = self.iin + [compile(config['CurrentInputs'][i], '<string>', 'eval')]

    self.tin = [] # temperatures
    for i in sorted(config['TemperatureInputs']):
      self.tin = self.tin + [config['TemperatureInputs'][i]]

    self.balf = [] # balance flags
    for i in sorted(config['BalanceFlags']):
      self.balf = self.balf + [config['BalanceFlags'][i]]

    self.chgstat = [] # balance flags
    for i in sorted(config['Status']):
      self.chgstat = self.chgstat + [config['Status'][i]]

      self.sampletime = time.time()
    self.getvi()
    self.batvoltsav = self.batvolts
    self.batcurrentav = self.current[-3]
    self.incurrentav = self.current[-2]
    self.batpwr1hrav = self.batvoltsav[-1]*self.batcurrentav/1000
    for i in range(0,self.numiins):
      self.currentav[i] = self.current[i]
#     (self.batvoltsav, self.current)

  def getvi(self):
    """ Get raw data """
    self.oldsampletime=self.sampletime
    sleeptime = max(config['sampling']['sampletime'] - (time.time()-self.oldsampletime), 0.0)
  #	     sleeptime
    time.sleep(sleeptime)
    self.sampletime = time.time()
# get data from Interfaces
    for i in config['Interfaces']:
      print (i)
      exec('self.'+i+".getdata()")
#    print (sorted(self.vin))
#    self.sortedvin=sorted(self.vin)
#    self.sortediin=sorted(self.iin)
    for i in range(len(self.iin)):
#      print (self.iin[i])
      self.current[i] = eval(self.iin[i]) \
                        *config['calibrate']['currentgain'][i] \
                        -config['calibrate']['currentoffset'][i]
#    self.batvolts[0] = self.rawdata.rawv[0]
#    self.uncalvolts[0] = self.rawdata.rawv[0]
#    self.batvolts[0] = 0.0
#    self.uncalvolts[0] = 0.0

    for i in range(len(self.vin)):
#      print (self.vin[i])
      self.uncalvolts[i+1] = eval(self.vin[i]) \
                           *config['calibrate']['batvgain'] # A/D to battery volts
      self.batvolts[i+1] = self.uncalvolts[i+1]*self.ratio[i] # calibrate values
#    print (self.batvolts,self.bms.rawdat)

    for i in range(len(self.tin)): # get temperatures
      self.temp[i] = eval(self.tin[i])

    for i in range(len(self.balf)): # get balance flags
      self.balflg[i] = eval(self.balf[i])

    for i in range(len(self.chgstat)): # get PIP charge states
      self.chargestates[i]=eval(self.chgstat[i])

  def getraw(self):
    """ gets battery data, do averaging, voltage results in volts, current in amps"""
    self.getvi()
#    print (self.batvolts)
    samplesav = config['sampling']['samplesav']
    self.deltatime=(self.sampletime-self.oldsampletime)/3600
    self.batah = self.currentav[-3]*self.deltatime
    self.batahadj = (self.currentav[-3]+config['battery']['ahloss'])*self.deltatime
    self.inah = self.currentav[-2]*self.deltatime
    batvoltsav = self.batvoltsav[config['battery']['numcells']]
    self.pwrin = self.inah*batvoltsav/1000 # gross input power
    self.pwrbat = self.batah*batvoltsav/1000 # battery power in/out
    self.batpwr1hrav = self.batpwr1hrav \
                    +(self.currentav[-3]*batvoltsav/1000-self.batpwr1hrav)/self.sampleshr # caculate battery power 1hr running av in kW

    for i in range(0,self.numiins):
      self.currentav[i] = (self.currentav[i]*(samplesav-1)+self.current[i])/samplesav # running av current
      if self.currentav[i] < 0:
        self.kWhin[i] = self.kWhin[i]+self.currentav[i]*self.deltatime*self.batvoltsav[numcells]/1000
      else:
        self.kWhout[i] = self.kWhout[i]+self.currentav[i]*self.deltatime*self.batvoltsav[numcells]/1000

    for i in range(1,numcells+1):
      self.batvoltsav[i] = (self.batvoltsav[i]*(samplesav-1) \
                           + self.batvolts[i])/samplesav
      if self.balflg[i-1]:
        self.baltime[i-1]= self.baltime[i-1]+self.deltatime # update time balancers are on
#    print (self.batvoltsav, self.currentav)
    self.deltav[0]=round(self.batvolts[0],3)
    self.lastmincellv=self.mincellv
    self.lastmaxcellv=self.maxcellv
    self.mincellv=100.0
    self.maxcellv=0.0
    for i in range(numcells,0,-1):
      self.deltav[i]=round((self.batvoltsav[i]-self.batvoltsav[i-1]-config['calibrate']['delta'][i-1]),3)
      self.mincellv = min(self.deltav[i],self.mincellv)
      self.maxcellv = max(self.deltav[i],self.maxcellv)
