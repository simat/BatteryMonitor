#!/usr/bin/python
# *****BatteryMonitor Getdata from battery cells getdata.py*****
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

from config import config
from summary import summary
IBatZero = 0.0   # 'Zero' battery current flow to calculate available power
minmaxdemandpwr = [0,0]
trackingsoc = -1.0  # target SOC if tracking battery SOC up and down, min=targetsoc

def initdemand(initsoc):
  """Initialise trackingsoc, must be called after initial SOC determined"""

  global trackingsoc
  trackingsoc = max(config['battery']['targetsoc'],initsoc+config['battery']['minsocdif'])

def solaravailable(batdata):
  """Returns max amount of surpus solar energy available without using battery Power
     Calculates the difference between amount of power being consumed vesus
     power that could be consumed to get battery current=IBatZero"""

  global minmaxdemandpwr, trackingsoc
  ibatminuteav=batdata.ibatminute/batdata.ibatnuminmin
  batdata.ibatminute = 0.0
  batdata.ibatnuminmin = 0

  soc=1-batdata.socadj/config['battery']['capacity']

  # calcualte power available as current I plus amount to get SOC to target in one minute
  iavailable=60*((1-trackingsoc)*config['battery']['capacity']-batdata.socadj)\
             -batdata.currentav[-3]
  pwravailable=iavailable*batdata.batvoltsav[config['battery']['numcells']+1]

  if config['battery']['tracksoc']:
    if soc < (trackingsoc - config['battery']['minsocdif'] - 0.01)\
       and not config['battery']['trackdown'] or\
       (soc < (trackingsoc - 0.01) and config['battery']['trackdown']):
       trackingsoc = max(config['battery']['targetsoc'],trackingsoc-0.01)
    elif soc>trackingsoc +config['battery']['minsocdif']:
      trackingsoc += 0.01
  else:
    trackingsoc=config['battery']['targetsoc']

  if soc<(trackingsoc - config['battery']['minsocdif'])
     or (config['DemandManager']['float?'] and
         summary['current']['state'][0]<>'Float'):
    minmaxdemandpwr[1]=0
  elif soc>=trackingsoc:
    minmaxdemandpwr[1]=min(config['DemandManager']['maxdemandpwr'],\
                       config['Inverters']['ratedoutput']*(batdata.pip.numinvon-1)\
                       +config['Inverters']['turnonslave']+500)
#  print ("ibat {} iavailable {} soc {} sodadj {} pwravail {} minmax {} trackSOC {}"\
#  .format(batdata.currentav[-3],iavailable,soc,batdata.socadj,pwravailable,minmaxdemandpwr,trackingsoc))
  return pwravailable,minmaxdemandpwr
