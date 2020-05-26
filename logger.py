# *****Logging Module logger.py*****
# Copyright (C) 2014-2018 Simon Richard Matthews
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

import logging
#logging.config.fileConfig('battery.cfg')
from config import loadconfig, config

errfile=logging.FileHandler(config['files']['errfile'])
errfile.setLevel(logging.DEBUG)
alarmfile=logging.FileHandler(config['files']['alarmfile'])
logfile=logging.FileHandler(config['files']['logfile'])


# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s,%(module)s,%(funcName)s,%(lineno)d')
alarmformat = logging.Formatter('%(asctime)s - %(message)s')
logformat = logging.Formatter('%(message)s')
# add formatter to ch
errfile.setFormatter(formatter)
alarmfile.setFormatter(alarmformat)
logfile.setFormatter(logformat)
# add ch to logger
