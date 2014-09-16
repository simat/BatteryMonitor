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

from config import config
numcells = config['battery']['numcells']
import time
import ADS1x15 as AtoD
AtoD0 = AtoD.ADS1x15(ic=0x01, debug=True)
AtoD1 = AtoD.ADS1x15(address=0x49,ic=0x01, debug=True)
AtoD2 = AtoD.ADS1x15(address=0x4A,ic=0x01, debug=True)

class Readings:
  """ get and manipulates readings from the real world"""
  
  measured = config['calibrate']['measured']
  displayed = config['calibrate']['displayed']
  avoffset = 0.0
  for i in range(1,numcells+1):
    avoffset = avoffset + measured[i]-displayed[i]
  avoffset = avoffset/numcells


  ratio = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  for i in range(1, numcells+1):
    ratio[i] = measured[i]/(displayed[i]+avoffset)
  calvolts = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

  measureddelta = config['calibrate']['measureddelta']
  displayeddelta = config['calibrate']['displayeddelta']

  calvolts = [measureddelta[i] - displayeddelta[i] for i in range(numcells+1)]
  deltav = [0.0, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25]
  rawvolts = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  batvolts = [0.0, 3.25, 6.5, 9.75, 13.00, 16.25, 19.50, 22.75, 26.00]
  uncalvolts = [0.0, 3.25, 6.5, 9.75, 13.00, 16.25, 19.50, 22.75, 26.00]
  batvoltsav = [0.0, 3.25, 6.5, 9.75, 13.00, 16.25, 19.50, 22.75, 26.00]
  rawcurrent = 0.0
  batcurrent = 0.0
  batcurrentav = 0.0
  soc = 0.0


  def getatod(self):
    """ Get data for A/Ds, calibrate, covert and place in list variables"""
    
    self.oldsampletime=self.sampletime
    sleeptime = max(config['sampling']['sampletime'] - (time.time()-self.oldsampletime), 0.0)
#	    print sleeptime
    time.sleep(sleeptime)
    self.sampletime = time.time()

    self.rawvolts[0] = AtoD2.readADCSingleEnded(channel=2, pga=2048, sps=250)/1000 # 0 volts

    for i in range(4):
      self.rawvolts[i+1] = AtoD0.readADCSingleEnded(channel=i, pga=2048, sps=250)/1000 # A to D 1 to 4 in volts
      self.rawvolts[i+5] = AtoD1.readADCSingleEnded(channel=i, pga=2048, sps=250)/1000 # A to D 5 to 8 in volts
    self.rawcurrent = AtoD2.readADCDifferential(chP=0, chN=1, pga=256, sps=250) # Battery current in counts
    self.batcurrent = self.rawcurrent*256.0/50.0  # current in mv
    self.batcurrent = self.batcurrent*250.0/50.0 # current in mamp
    self.batvolts[0] = self.rawvolts[0]
    self.uncalvolts[0] = self.rawvolts[0]
    for i in range(1,numcells+1):
      self.uncalvolts[i] = self.rawvolts[i]*(2.49+33.2)/2.49 # A/D to battery volts
      self.batvolts[i] = self.uncalvolts[i]*self.ratio[i] +self.avoffset # calibrate values


  def __init__(self):
    self.sampletime = time.time()
    self.getatod()
    self.batvoltsav = self.batvolts
    self.batcurrentav = self.batcurrent


  def getraw(self):
    """ gets battery data, do averaging, voltage results in volts, current in milliamps"""
    self.getatod()

    samplesav = config['sampling']['samplesav']
    self.batcurrentav = (self.batcurrentav*(samplesav-1)+self.batcurrent)/samplesav # running av current
    for i in range(1,numcells+1):   
      self.batvoltsav[i] = (self.batvoltsav[i]*(samplesav-1) + self.batvolts[i])/samplesav

    self.deltav[0]=round(self.batvolts[0],3)
    for i in range(numcells,0,-1):
      self.deltav[i]=round((self.batvoltsav[i]-self.batvoltsav[i-1]+self.calvolts[i]),3)

