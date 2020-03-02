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
IBatZero = 0.5   # 'Zero' battery current flow to calculate available power


def solaravailable():
  """Returns max amount of surpus solar energy available without using battery Power
     Calculates the difference between amount of power being consumed vesus
     power that could be consumed to get battery current=IBatZero"""

  ibatminuteav=batdata.ibatminute/batdata.ibatnuminmin
  batdata.ibatminute = 0.0
  batdata.ibatnuminmin = 0

  iavailable=(IBatZero-ibatminuteav)
  soc=1-batdata.socadj/config['battery']['capacity']
  iavailable=iavailable+config['battery']['maxchargerate']*20*(0.95-soc)
  pwravailable=iavailable*batdata.batvoltsav[batdata.numcells+1]
  return pwravailable
