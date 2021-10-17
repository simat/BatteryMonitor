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
IBatZero = 0.0   # 'Zero' battery current flow to calculate available power
minmaxdemandpwr = [0,0]

def solaravailable(batdata):
  """Returns max amount of surpus solar energy available without using battery Power
     Calculates the difference between amount of power being consumed vesus
     power that could be consumed to get battery current=IBatZero"""

  global minmaxdemandpwr
  ibatminuteav=batdata.ibatminute/batdata.ibatnuminmin
  batdata.ibatminute = 0.0
  batdata.ibatnuminmin = 0

  minsoc = config['battery']['targetsoc'] -config['battery']['minsocdif']
  soc=1-batdata.socadj/config['battery']['capacity']

  """  iavailable=(IBatZero-ibatminuteav)
  #iavailable=iavailable+config['battery']['maxchargerate']* \
  #           (soc-config['battery']['targetsoc'])*20
  iavailable=(soc\
             -config['battery']['targetsoc'])*config['battery']['capacity']\
             *config['DemandManager']['socfeedback'] \
             -ibatminuteav*config['DemandManager']['currentfeedback']"""

  # calcualte power available as current I plus amount to get SOC to target in one minute
  iavailable=60*((1-config['battery']['targetsoc'])*config['battery']['capacity']-batdata.socadj)\
             -batdata.currentav[-3]
  pwravailable=iavailable*batdata.batvoltsav[config['battery']['numcells']+1]
  if soc<minsoc:
    minmaxdemandpwr[1]=0
  elif soc>=config['battery']['targetsoc']:
    minmaxdemandpwr[1]=config['DemandManager']['maxdemandpwr']
  print ("ibat {} iavailable {} soc {} sodadj {} pwravail {} minmax {}".format(batdata.currentav[-3],iavailable,soc,batdata.socadj,pwravailable,minmaxdemandpwr))

  return pwravailable,minmaxdemandpwr
