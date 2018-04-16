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

import time
import serial
import binascii


def getbmsdat(port,command):
  """ Issue BMS command and return data as byte data """
  """ assumes data port is open and configured """
  port.write(command)
  reply = port.read(4)

  print (reply)
  x = int.from_bytes(reply[3:5], byteorder = 'big')
  print (x)
  data = port.read(x)
  end = port.read(3)
  print (data)
  return data

def x(port):
  """ Get data from BMS board"""
  ser = serial.Serial(port)  # open serial port
  ser.timeout = 3
  command = bytes.fromhex('DD A5 03 00 FF FD 77')
  dat = getbmsdat(ser,command)
  rawi = int.from_bytes(dat[2:4], byteorder = 'big',signed=True)
  print ("I=",rawi)
#  line1 = [ 0 for i in range(int(len(dat)))]
#  for i in range(0,int(len(dat))):
#    print (dat[i*2:i*2+2])
#    print (int.from_bytes(dat[i:i+1], byteorder = 'big'))
#    line1[i] = int.from_bytes(dat[i:i+1], byteorder = 'big')
  print (binascii.hexlify(dat))
#  print (line1)


  # voltages
  command = bytes.fromhex('DD A5 04 00 FF FC 77')
  voltages = getbmsdat(ser,command)
  ser.close
  print (binascii.hexlify(voltages))
  rawv = [ 0.0 for i in range(15)]
  for i in range(15):
    rawv[i] = int.from_bytes(voltages[i*2:i*2+2], byteorder = 'big')/1000.00
    rawv[i] = rawv[i]+rawv[i-1]
  print (rawv)
