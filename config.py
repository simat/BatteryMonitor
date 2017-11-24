# *****BatteryMonitor parse Config data from battery config file*****
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

from ast import literal_eval
from configparser import SafeConfigParser

config ={}
def loadconfig():
    configfile = SafeConfigParser()
    configfile.read('battery.cfg')
    for section in configfile.sections():
      config[section] = {}
      for key, val in configfile.items(section):
        config[section][key] = literal_eval(val)

loadconfig()


