
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

import Adafruit_BBIO.GPIO as gpio
import Adafruit_BBIO.ADC as adc
adc.setup()

class Rawdat():
  """class for using the raspberry Pi for IO"""

  def __init__(self):
    gpio.setup("P9_41", gpio.OUT)
    adc.setup()
    self.rawdat={'ADCP9_39':0.0}

  def chargeonoff(self,onoroff):
    gpio.output("P9_41",onoroff)

  def getdata(self):
    self.rawdat['ADCP9_39'] = adc.read("P9_39")
    print (self.rawdat['ADCP9_39'])
