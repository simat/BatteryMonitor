# *****BatteryMonitor main file batteries.py*****
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


#!/usr/bin/python
import sys

import serial
import binascii
from config import config

import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)


class Alarms:
  # Initialise and compile alarms
  def __init__(self):
    self.alarmtriggered={}
    for i in config['alarms']:
      self.alarmtriggered[i]=False
      exec(config['alarms'][i][0])
"""      config['alarms'][i][1] = compile(config['alarms'][i][1], '<string>', 'exec')
      config['alarms'][i][2] = compile(config['alarms'][i][2], '<string>', 'exec')
      config['alarms'][i][3] = compile(config['alarms'][i][3], '<string>', 'exec')
      config['alarms'][i][4] = compile(config['alarms'][i][4], '<string>', 'exec')"""
      
  def scanalarms(self,batdata):
    for i in config['alarms']:
      exec(config['alarms'][i][1])
#      log.debug('{}{}{}'.format(self.test,batdata.maxcellv,batdata.lastmaxcellv))
      if self.test:
  #            sys.stderr.write('Alarm 1 triggered')
        log.debug('alarm triggered')
        self.alarmtriggered[i]=True
        exec(config['alarms'][i][2])
      exec(config['alarms'][i][3])
      if self.test:
        log.debug('alarm reset')
        self.alarmtriggered[i]=False
        exec(config['alarms'][i][4])
