#!/usr/bin/python
# *****BatteryMonitor Summary Generator*****
# Copyright (C) 2020 Simon Richard Matthews
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

"""this program generates the summary file from the config data in battery.cfg"""

from config import config
from os import path,remove

zerovolts=[0.0 for i in range(config['battery']['numcells']+1)]
fivevolts=[5.0 for i in range(config['battery']['numcells']+1)]
fivevolts[-1]=5.0*config['battery']['numcells']
zeroamps=[0.0 for i in range(len(config['CurrentInputs']))]
inverterstate=['Offline' for i in range(config['Inverters']['numinverters'])

section={}
section['timestamp']=20140101000000
section['maxvoltages'],section['maxnocharge']=zerovolts,zerovolts
section['minnoload'],section['minvoltages']=fivevolts,fivevolts
section['deltav']=[5.0,0.0,0.0]
section['ioutmax'],section['kwoutmax'],section['kwhout']=zeroamps,zeroamps,zeroamps
section['iinmax'],section['kwinmax'],section['kwhin']=zeroamps,zeroamps,zeroamps
section['ah']=[10000.0, 0.0, -1000.0, 0.0, 0.0, 0.0, 0.0]
section['dod']=[10000.0, 0.0, -1000.0, 0]
section['power']=[0.0, 0.0, 0.0, 0]
section['tmax']=[-60.0 for i in range(len(config['TemperatureInputs']))]
section['tmin']=[120.0 for i in range(len(config['TemperatureInputs']))]
section['baltime']=[ 0.0 for i in range(config['battery']['numcells'])]

order='timestamp',\
      'maxvoltages',\
      'maxnocharge',\
      'minnoload',\
      'minvoltages',\
      'deltav',\
      'ioutmax',\
      'kwoutmax',\
      'kwhout',\
      'iinmax',\
      'kwinmax',\
      'kwhin',\
      'ah',\
      'dod',\
      'power',\
      'tmax',\
      'tmin',\
      'baltime'

endcurrent="""state = {}
batpwr1hrav = [0]
excesssolar = [0]
minmaxdemandpwr = [0, {}]
""".format(inverterstate,config['DemandManager']['maxdemandpwr'])

template=['[current]','[hour]','[currentday]','[prevday]','[monthtodate]',
          '[yeartodate]','[alltime]']

def writesummaryfile():
  """ writes summary file to disk"""
  with open (config['files']['summaryfile'],'x') as summaryfile:
    for i in (template):
      summaryfile.write('{}\n'.format(i))
      for items in range(len(order)):
        summaryfile.write('{}={}\n'.format(order[items],section[order[items]]))
      if i=='[current]':
        summaryfile.write(endcurrent)
      summaryfile.write('\n')


try:
  with open (config['files']['summaryfile'],'x') as summaryfile:
    writesummaryfile()
except FileExistsError:
  x=input('Summary file exists, do you want to overwrite it?[y]')
  if not x or x=='y' or x=='Y':
    remove(config['files']['summaryfile'])
    writesummaryfile()
  else:
    exit()
