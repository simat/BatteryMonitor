
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


  def __init__(self):
    self.measured = config['calibrate']['measured']
    self.displayed = config['calibrate']['displayed']

    self.ratio = [ 1.0 for i in range(numcells+1)]
    for i in range(1, numcells+1):
      self.ratio[i] = self.measured[i]/self.displayed[i]
    self.calvolts = [ 0.0 for i in range(numcells+1)]

    #  calvolts = [measureddelta[i] - displayeddelta[i] for i in range(numcells+1)]
    self.deltav = [ 3.25 for i in range(numcells+1)]
    self.deltav[0] = 0.0
    self.rawvolts = [ 0.0 for i in range(numcells+1)]
    self.batvolts = [ i*3.25 for i in range(numcells+1)]
    self.uncalvolts = [ i*3.25 for i in range(numcells+1)]
    self.batvoltsav = [ i*3.25 for i in range(numcells+1)]
    self.balflg = [ 0.0 for i in range(numcells)]
    self.baltime = [ 0.0 for i in range(numcells)]
    self.temp = [ 0.0 for i in range(len(config['TemperatureInputs']))]
    self.numiins = len(config['CurrentInputs'])
    self.current = [ 0.0 for i in range(self.numiins)]
    self.currentav = [ 0.0 for i in range(self.numiins)]
    self.kWhin = [ 0.0 for i in range(self.numiins)]
    self.kWhout = [ 0.0 for i in range(self.numiins)]
    self.chargestates = [ b'00' for i in range(len(config['Status']))]

    #  rawcurrent = 0.0
    #  batcurrent = 0.0
    #  batcurrentav = 0.0
    #  rawincurrent = 0.0
    #  incurrent = 0.0
    #  incurrentav = 0.0
    self.soc = 0.0
    self.socadj = 0.0
    self.batah = 0.0
    self.batahadj = 0.0
    self.inah = 0.0
    self.inahtot = 0.0
    self.ah = 0.0

    self.mincellv=100.0
    self.maxcellv=0.0
    self.lastmaxv = 0.0 # previous sample maximum cell voltage
    self.lastminv = 100.0 # previous sample minimum cell voltage
    self.pwrbat = 0.0 # battery power units kW
    self.pwrbattot = 0.0  # total battery power units kWh
    self.pwrin = 0.0  # gross power in units kW
    self.pwrintot = 0.0 # total gross power in units kWh
    self.iall=""
    self.vdelta=""
    self.vcells=""
    self.soctxt=""
    self.socadjtxt=""
    self.sampleshr=3600/config['sampling']['sampletime'] # numder of sample / hour
    batpwr1hrav = 0.0

    for i in config['Interfaces']:
      interface=re.match(r'\w*',config['Interfaces'][i]).group()
      snstring=re.compile(r'[(].*[^)]')
      sn=snstring.search(config['Interfaces'][i])
      if sn!=None:
        sn=sn.group()
      exec("import " + interface)
      if sn==None:
        exec('self.'+i +'='+interface+'.Rawdat()')
      else:
        exec('self.'+i+'='+interface+".Rawdat('"+str(sn[1:])+"')")

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
      exec('self.'+i+".getdata()")
    for i in range(len(self.iin)):
      self.current[i] = eval(self.iin[i]) \
                        *config['calibrate']['currentgain'][i] \
                        -config['calibrate']['currentoffset'][i]
#    self.batvolts[0] = self.rawdata.rawv[0]
#    self.uncalvolts[0] = self.rawdata.rawv[0]
#    self.batvolts[0] = 0.0
#    self.uncalvolts[0] = 0.0

    for i in range(len(self.vin)):
      self.uncalvolts[i+1] = eval(self.vin[i]) \
                           *config['calibrate']['batvgain'] # A/D to battery volts
      self.batvolts[i+1] = self.uncalvolts[i+1]*self.ratio[i] # calibrate values

    for i in range(len(self.tin)): # get temperatures
      self.temp[i] = eval(self.tin[i])

    for i in range(len(self.balf)): # get balance flags
      self.balflg[i] = eval(self.balf[i])

    for i in range(len(self.chgstat)): # get PIP charge states
      self.chargestates[i]=eval(self.chgstat[i])

  def getraw(self):
    """ gets battery data, do averaging, voltage results in volts, current in amps"""
    self.getvi()
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
    self.deltav[0]=round(self.batvolts[0],3)
    self.lastmincellv=self.mincellv
    self.lastmaxcellv=self.maxcellv
    self.mincellv=100.0
    self.maxcellv=0.0
    for i in range(numcells,0,-1):
      self.deltav[i]=round((self.batvoltsav[i]-self.batvoltsav[i-1]-config['calibrate']['delta'][i-1]),3)
      self.mincellv = min(self.deltav[i],self.mincellv)
      self.maxcellv = max(self.deltav[i],self.maxcellv)
