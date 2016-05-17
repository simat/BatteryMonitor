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
from ConfigParser import SafeConfigParser
from config import config
numcells = config['battery']['numcells']
voltages = []
avv = []

summaryfile = SafeConfigParser()

def tail(file, n=1, bs=1024):
    f = open(file)
    f.seek(-1,2)
    l = 1-f.read(1).count('\n') # If file doesn't end in \n, count it anyway.
    B = f.tell()
    while n >= l and B > 0:
            block = min(bs, B)
            B -= block
            f.seek(B, 0)
            l += f.read(block).count('\n')
    f.seek(B, 0)
    l = min(l,n) # discard first (incomplete) line if l > n
    lines = f.readlines()[-l:]
    f.close()
    return lines

def avv():
  vstr=""
  v=[0.0 for i in range(numcells)]
  endlog=tail(config['files']['logfile'],11)
  for j in range(numcells):
    for i in range(10):
      x=float(endlog[i][j*6+15:j*6+20])	
      v[j]=v[j]+x
  for i in range(len(v)):
    v[i]=v[i]/10
    vstr=vstr+str(i+1) + "=" +str(round(v[i],3)).ljust(5,'0') + ", "
  print vstr
  print config['calibrate']['delta']
  return v



def getv():
  global voltages
  try:
    summaryfile.read(config['files']['summaryfile'])
  except IOError:
    pass
  voltages=literal_eval(summaryfile.get('current','maxvoltages'))
  vprint = ''
  for i in range(numcells+1):
    vprint = vprint + str(i+1) + '=' + str(voltages[i]).ljust(5,'0') + ', '
  print vprint
  print config['calibrate']['delta']
  
def main():
  avvolts=[]
  while True:
    try:
      avvolts=avv()
#      time.sleep(60.0)
      what = raw_input(">")
      if len(what)>0:
        realvolts = input("Cell " + what + " reading ")
        what=int(what)
        config['calibrate']['delta'][what-1] = round(avvolts[what-1]-realvolts+config['calibrate']['delta'][what-1],3)
        print config['calibrate']['delta']
        batconfigdata=SafeConfigParser()
        batconfigdata.read('battery.cfg')
        batconfigdata.set('calibrate','delta',str(config['calibrate']['delta']))
        with open('battery.cfg', 'w') as batconfig:
          batconfigdata.write(batconfig)
        batconfig.closed


    except KeyboardInterrupt:
      break

