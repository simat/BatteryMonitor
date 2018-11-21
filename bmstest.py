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
import json

class Bms:
  def __init__(self):
    self.bmsconfig={}
    self.bmsconfig=self.rdjson('bms.json')

  def wrjson(self,file,data):
    with open(file, "w") as write_file:
      json.dump(data,write_file,indent=2)

  def rdjson(self,file):
    with open(file, "r") as read_file:
      data=json.load(read_file)
    return data

  def rdallconfig(self,port='/dev/ttyUSB0'):
    "reads BMS data from BMS board and stores in template self.bmsconfig"

    for i in self.bmsconfig:
      list=[]
      list.append(i)
      self.configitems(list)

  def getbmsdat(self,port,command):
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

  def getcmd(self):
    """gets command from user"""
    command=str(input("Enter Command>"))
    return command

  def loop(self):
    while True:
      self.main()

  def main(self,port='/dev/ttyUSB0'):
      ser = self.openbms(port)
      command=bytes.fromhex(self.getcmd())
      self.getbmsdat(ser,command)
      ser.close

  def openbms(self,port='/dev/ttyUSB0'):
      ser = serial.Serial(port)  # open serial port
      ser.timeout = 3
      return ser

  def switchfets(self,port='/dev/ttyUSB0'):
    """ switch charge and discharge fets """
    print ('(00)=Both FETs off')
    print ('(01)=Charge FET on, Discharge FET off')
    print ('(02)=Charge FET off, Discharge FET on')
    print ('(03)=Both FETs on')
    usercmd = input("Enter numeric option> ")
    ser = self.openbms(port)
    command = bytes.fromhex('DD 5A 00 02 56 78 FF 30 77')
    self.getbmsdat(ser,command)
    usercmd=b'\xE1\x02\x00'+bytes.fromhex(usercmd)
    command = b'\xDD\x5A'+usercmd+self.crccalc(usercmd).to_bytes(2, byteorder='big')+b'\x77'
    self.getbmsdat(ser,command)
    command = bytes.fromhex('DD 5A 01 02 00 00 FF FD 77')
    self.getbmsdat(ser,command)


  def configitems(self,list,port='/dev/ttyUSB0',write=False):
    """ returns read or write data from all data registers in list"""

    ser = self.openbms(port)
    command = bytes.fromhex('DD A5 03 00 FF FD 77')
    print ('command=',binascii.hexlify(command))
    data=self.getbmsdat(ser,command)
    print ('reply=',binascii.hexlify(data))
    command = bytes.fromhex('DD A5 04 00 FF FC 77')
    print ('command=',binascii.hexlify(command))
    data=self.getbmsdat(ser,command)
    print ('reply=',binascii.hexlify(data))
    command = bytes.fromhex('dd 5a 00 02 56 78 ff 30 77')
    print ('command=',binascii.hexlify(command))
    data=self.getbmsdat(ser,command)
    print ('reply=',binascii.hexlify(data))

    for configitem in list:
      print (configitem)

      if write:
        packet=bytes.fromhex(self.bmsconfig[configitem]['reg'])+b'\x02' \
        +self.bmsconfig[configitem]['value'].to_bytes(2, byteorder='big')
        packet=b'\xDD\x5A'+packet+self.crccalc(packet).to_bytes(2, byteorder='big')+b'\x77'
      else:
        packet=bytes.fromhex(self.bmsconfig[configitem]['reg'])+b'\x00'
        packet=b'\xDD\xA5'+packet+self.crccalc(packet).to_bytes(2, byteorder='big')+b'\x77'
      print ('command=',binascii.hexlify(packet))
      data=self.getbmsdat(ser,packet)
      self.bmsconfig[configitem]['value']=int.from_bytes(data, byteorder = 'big')
      print ('register reply=',binascii.hexlify(data),int.from_bytes(data, byteorder = 'big'))
    command = bytes.fromhex('dd 5a 01 02 00 00 ff fd 77')
    print ('command=',binascii.hexlify(command))
    data=self.getbmsdat(ser,command)
    print ('reply=',binascii.hexlify(data))

  def getdat(self,port='/dev/ttyUSB0'):
    """ Get data from BMS board"""
    ser = self.openbms(port)
    command = bytes.fromhex('DD A5 03 00 FF FD 77')
    dat = self.getbmsdat(ser,command)
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
    voltages = self.getbmsdat(ser,command)
    ser.close
    print (binascii.hexlify(voltages))
    rawv = [ 0.0 for i in range(15)]
    for i in range(15):
      rawv[i] = int.from_bytes(voltages[i*2:i*2+2], byteorder = 'big')/1000.00
      rawv[i] = rawv[i]+rawv[i-1]
    print (rawv)

    command = bytes.fromhex('DD A5 05 00 FF FB 77')
    dat = self.getbmsdat(ser,command)

  #  line1 = [ 0 for i in range(int(len(dat)))]
  #  for i in range(0,int(len(dat))):
  #    print (dat[i*2:i*2+2])
  #    print (int.from_bytes(dat[i:i+1], byteorder = 'big'))
  #    line1[i] = int.from_bytes(dat[i:i+1], byteorder = 'big')
    print (binascii.hexlify(dat))
  #  print (line1)

  def crccalc(self,data):
    """returns crc as integer from byte stream"""
    crc=0x10000
    for i in data:
      crc=crc-int(i)
    return crc

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
      self.loop()
