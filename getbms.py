#!/usr/bin/python
# *****BatteryMonitor Getdata from battery cells getdata.py*****
# Copyright (C) 2017 Simon Richard Matthews
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


import serial
import binascii
from config import config
numcells = config['battery']['numcells']

class Raw:
  # compile analog capture code to save CPU time
  vin = []
  for i in sorted(config['VoltageInputs']):
    vin = vin + [compile(config['VoltageInputs'][i], '<string>', 'eval')]
  #  vin = vin + [config['VoltageInputs'][i]]
  #for i in config['CurrentInputs']:
  #  config['CurrentInputs'][i] = compile(config['CurrentInputs'][i], '<string>', 'eval')
  iin = []
  for i in sorted(config['CurrentInputs']):
    iin = iin + [compile(config['CurrentInputs'][i], '<string>', 'eval')]

  line1 = [ 0 for i in range(20)]
  rawi = [0.0, 0.0, 0.0]
  rawv = [ 0.0 for i in range(numcells+1)]

  def getbmsdat(self,port,command):
    """ Issue BMS command and return data as byte data """
    """ assumes data port is open and configured """
    port.write(command)
    reply = port.read(4)
  #  print (reply)
    x = int.from_bytes(reply[3:5], byteorder = 'big')
#    print (x)
    data = port.read(x)
    end = port.read(3)
#    print (data)
    return data

  def x(self):
    """ Get data from BMS board"""
    ser = serial.Serial(config['files']['usbport'])  # open serial port
    ser.timeout = 3
    command = bytes.fromhex('DD A5 03 00 FF FD 77')
    dat = self.getbmsdat(ser,command)
    self.rawi[0] = int.from_bytes(dat[2:4], byteorder = 'big')
#    print (self.rawi)
#    self.line1 = [ 0 for i in range(int(len(dat)))]
#    for i in range(0,int(len(dat))):
  #    print (dat[i*2:i*2+2])
  #    print (int.from_bytes(dat[i:i+1], byteorder = 'big'))
#      self.line1[i] = int.from_bytes(dat[i:i+1], byteorder = 'big')
#    print (binascii.hexlify(dat))
#    print (self.line1)


  # voltages
    x = 'DD A5 04 00 FF FC 77'
    command = bytes.fromhex('DD A5 04 00 FF FC 77')
    voltages = self.getbmsdat(ser,command)
    for i in range(0,numcells):
      self.rawv[i+1] = int.from_bytes(voltages[i*2:i*2+2], byteorder = 'big')\
                       /1000.00
      self.rawv[i+1] = self.rawv[i+1]+self.rawv[i]
  #  print (self.rawv)
  #  print (binascii.hexlify(voltages))
