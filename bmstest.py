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
  print (command)
  port.write(command)
  reply = port.read(4)

  print (reply)
  x = int.from_bytes(reply[3:5], byteorder = 'big')
  print (x)
  data = port.read(x)
  end = port.read(3)
  print (data)
  print (binascii.hexlify(data))
  return data

def getcmd():
  """gets command from user"""
  command=str(input("Enter Command>"))
  return command

def loop():
  while True:
    main()

def main(port='/dev/ttyUSB0'):
    ser = openbms(port)
    command=bytes.fromhex(getcmd())
    getbmsdat(ser,command)
    ser.close

def openbms(port='/dev/ttyUSB0'):
    ser = serial.Serial(port)  # open serial port
    ser.timeout = 3
    return ser

def switchfets(port='/dev/ttyUSB0'):
  ser = openbms(port)
  command = bytes.fromhex('DD 5A 00 02 56 78 FF 30 77')
  getbmsdat(ser,command)
  command = bytes.fromhex('DD 5A E1 02 00 00 FF 1D 77')
  getbmsdat(ser,command)
  command = bytes.fromhex('DD 5A 01 02 00 00 FF FD 77')
  getbmsdat(ser,command)


def getdat(port='/dev/ttyUSB0'):
  """ Get data from BMS board"""
  ser = openbms(port)
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

  command = bytes.fromhex('DD A5 05 00 FF FB 77')
  dat = getbmsdat(ser,command)

#  line1 = [ 0 for i in range(int(len(dat)))]
#  for i in range(0,int(len(dat))):
#    print (dat[i*2:i*2+2])
#    print (int.from_bytes(dat[i:i+1], byteorder = 'big'))
#    line1[i] = int.from_bytes(dat[i:i+1], byteorder = 'big')
  print (binascii.hexlify(dat))
#  print (line1)

if __name__ == "__main__":
  """if run from command line, piptest [command] [port]
  default port /dev/ttyUSB1, if no command ask user"""

  print (sys.argv)
  if len(sys.argv) == 2:
    sendcmd(sys.argv[1])
  else:
    if len(sys.argv) == 3:
      sendcmd(sys.argv[1],sys.argv[2])
    else:
      loop()
