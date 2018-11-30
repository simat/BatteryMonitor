#!/usr/bin/python
# *****Core routines to retrieve and store data to BMS PCBs*****
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
import json

def rdjson(file):
  with open(file, "r") as read_file:
    data=json.load(read_file)
  return data

configinmem={}  # template for bms data
configinmem=rdjson('bms.json')
fullconfiglist= [configinmem[i] for i in configinmem]

def wrjson(file,data):
  with open(file, "w") as write_file:
    json.dump(data,write_file,indent=2)

def crccalc(data):
  """returns crc as integer from byte stream"""
  crc=0x10000
  for i in data:
    crc=crc-int(i)
  return crc


def rdallconfig(port='/dev/ttyUSB0'):
  "reads BMS data from BMS board and stores in template configinmem"

  configitems(list)

def openbms(port='/dev/ttyUSB0'):
    ser = serial.Serial(port)  # open serial port
    ser.timeout = 3
    return ser

def getbmsdat(port,command):
  """ Issue BMS command and return data as byte data """
  """ assumes data port is open and configured """
#  print (command)
  port.write(command)
  reply = port.read(4)

#  print (reply)
  x = int.from_bytes(reply[3:5], byteorder = 'big')
#  print (x)
  data = port.read(x)
  end = port.read(3)
#  print (data)
#  print (binascii.hexlify(data))
  return data

def configitems(list,port='/dev/ttyUSB0',write=False):
  """ returns read or write data from all data registers in list"""
  global configinmem
  ser = openbms(port)
  command = bytes.fromhex('DD A5 03 00 FF FD 77')
  print ('command=',binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))
  command = bytes.fromhex('DD A5 04 00 FF FC 77')
  print ('command=',binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))
  command = bytes.fromhex('dd 5a 00 02 56 78 ff 30 77')
  print ('command=',binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))

  for configitem in list:
    print (configitem)

    if write:
      packet=bytes.fromhex(configitem['reg'])+b'\x02' \
      +configitem['value'].to_bytes(2, byteorder='big')
      packet=b'\xDD\x5A'+packet+crccalc(packet).to_bytes(2, byteorder='big')+b'\x77'
    else:
      packet=bytes.fromhex(configitem['reg'])+b'\x00'
      packet=b'\xDD\xA5'+packet+crccalc(packet).to_bytes(2, byteorder='big')+b'\x77'
    print ('command=',binascii.hexlify(packet))
    data=getbmsdat(ser,packet)
    configitem['value']=int.from_bytes(data, byteorder = 'big')
    print ('register reply=',binascii.hexlify(data),int.from_bytes(data, byteorder = 'big'))
  command = bytes.fromhex('dd 5a 01 02 00 00 ff fd 77')
  print ('command=',binascii.hexlify(command))
  print ('reply=',binascii.hexlify(data))
