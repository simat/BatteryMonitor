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
fullconfiglist= [i for i in configinmem]

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
<<<<<<< HEAD
    ser.timeout = 1
    return ser

def getbmsdat(port,command):
  """ Issue BMS command and return data as byte data """
  """ assumes data port is open and configured """
  print ('command=',binascii.hexlify(command))
  port.write(command)
  reply = port.read(4)
  x = int.from_bytes(reply[3:5], byteorder = 'big')
  data = port.read(x)
  end = port.read(3)
  if len(data)<x:
    print ('Serial Timeout')
  if crccalc(reply[2:4]+data)!=int.from_bytes(end[0:2],byteorder ='big') and x!=0:
    print('CRC Error')
  print ('reply=',binascii.hexlify(data))
  return data

def configitems(list,port='/dev/ttyUSB0',write=False,calibrate=False):
  """ returns read or write data from all data registers in list
      skips any items if calibrate=False and read?=False """
  global configinmem
  ser = openbms(port)
  command = bytes.fromhex('DD A5 03 00 FF FD 77')
  data=getbmsdat(ser,command)
  command = bytes.fromhex('DD A5 04 00 FF FC 77')
  data=getbmsdat(ser,command)
  command = bytes.fromhex('dd 5a 00 02 56 78 ff 30 77')
  data=getbmsdat(ser,command)

#  command = bytes.fromhex('DD A5 2E 00 FF D2 77')
#  data=getbmsdat(ser,command)
  valueint=0
  valuefloat=0.0
  valueascii=''
  valuebin='0b0'

  for configitem in list:
    print (configitem)
    if configinmem[configitem]['read?'] or calibrate:
      if write:
        value=configinmem[configitem]['value']
        if "valueint" in configinmem[configitem]['encode']:
          packetlength=b'\x02'
          valueint=int(value)
        elif "valuefloat" in configinmem[configitem]['encode']:
          packetlength=b'\x02'
          valuefloat=float(value)
        elif "valuebin" in configinmem[configitem]['encode']:
          packetlength=b'\x02'
          valuebin=value
        else:
          valueascii=value
          packetlength=(len(value)+1).to_bytes(1,'big')+len(value).to_bytes(1,'big')
        packet=bytes.fromhex(configinmem[configitem]['reg'])+packetlength \
        +eval(configinmem[configitem]['encode'])
        packet=b'\xDD\x5A'+packet+crccalc(packet).to_bytes(2, byteorder='big')+b'\x77'
        getbmsdat(ser,packet)
      else:
        packet=bytes.fromhex(configinmem[configitem]['reg'])+b'\x00'
        packet=b'\xDD\xA5'+packet+crccalc(packet).to_bytes(2, byteorder='big')+b'\x77'
        value=getbmsdat(ser,packet)
        valueascii=value.decode("Latin-1")
        valueint=int.from_bytes(value, byteorder = 'big')
        configinmem[configitem]['value']=eval(configinmem[configitem]['decode'])
        print ('register reply=',binascii.hexlify(value),int.from_bytes(value, byteorder = 'big'))

  if write:
    command = bytes.fromhex('dd 5a 01 02 28 28 ff ad 77')
    data=getbmsdat(ser,command)
#    command = bytes.fromhex('dd a5 aa 00 ff 56 77')
#    data=getbmsdat(ser,command)"""
  else:
    command = bytes.fromhex('dd 5a 01 02 00 00 ff fd 77')
    data=getbmsdat(ser,command)
