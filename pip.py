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
import sys

import serial
import binascii
from config import config
numcells = config['battery']['numcells']

class Rawdat:

  def __init__(self):
    self.rawdat ={'BInI':0.0,'BOutI':0.0,'BV':0.0,'PVI':0.0,'PVW':0,'ACW':0.0,'ChgStat':00}

  def getdata(self):
    """returns dictionary with data from Pip4048"""

    self.openpip(config['files']['pipport'])
    reply=self.sendcmd('QPIGS',110)
    self.rawdat['BInI']=reply[47:50]
    self.rawdat['BOutI']=reply[77:82]
    self.rawdat['PVI']=reply[60:64]
    self.rawdat['BV']=reply[41:46]
    self.rawdat['ACW']=reply[28:32]
    reply=self.sendcmd('Q1',74)
    self.rawdat['ChgStat']=reply[-5:-3]
    self.rawdat['PVW']=reply[53:56]
    self.port.close()

  def openpip(self,port):
    self.port = serial.Serial(port,baudrate=2400,timeout=2)  # open serial port

  def crccalc(self,command):
    """returns crc as integer from binary string command"""

    crc=binascii.crc_hqx(command,0)
    crchi=crc>>8
    crclo=crc&255

    if crchi == 0x28 or crchi==0x0d or crchi==0x0a:
      crc+=256

    if crclo == 0x28 or crclo==0x0d or crclo==0x0a:
      crc+=1
    return crc

  def sendcmd(self,command,replylen):
    """send command/query to Pip4048, return reply"""


    for i in range(5):
      try:
        command=command.encode('ascii','strict')
        crc=self.crccalc(command)
        command=command+crc.to_bytes(2, byteorder='big')+b'\r'
        self.port.write(command)
        reply = self.port.read(replylen)
        if  self.crccalc(reply[0:-3]) != int.from_bytes(reply[-3:-1],byteorder='big'):
          raise IOError("CRC error in Pip4048 return string")
          break
      except IOError as err:
        print(err.args)
        if i==4:
          raise
      return reply

  def setparam(self,command,replylen):
    reply=self.sendcmd(command,replylen)
    if reply[1:4]!=b'ACK':
      raise IOError('Bad Parameters')
