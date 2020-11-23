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
import RPi.GPIO as gpio
import threading
from time import sleep


class Rawdat():
  """class for using the raspberry Pi for IO"""

  savedinvertermap ={}

  def __init__(self):
    self.gpio=gpio
    self.gpio.setmode(self.gpio.BOARD)

  def getdata(self):
    pass

  def backgroundswapinv(self,on,off):
    print(on,off)
    self.gpio.output(on,0)
    sleep(20) # wait for second inverter to power up and syncronise
    self.gpio.output(off,1)

  def swapinverter(self,on,off):
    """turns on inverter controlled by Pi pin number if on arg and turns off
       inverter controlled by Pi pin number in off arg"""
    threading.Thread(target=self.backgroundswapinv,args=(self,on,off)).start()

  def allinvon(self,pins):
    """ turn on inverters in pins list, save current inverter map"""

    global savedinvertermap
    for pin in pins:
      self.savedinvertermap[pin]=self.gpio.input(pin)
      self.gpio.output(pin,0)

  def restoreinverters(self):
    """ restore saved invertermap"""
    for pin in savedinvertermap:
      self.gpio.output(pin,self.savedinvertermap[pin])
