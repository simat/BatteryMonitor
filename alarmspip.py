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

class Alarms:
  # Initialise and compile alarms
  def __init__(self):
    self.overvflg=False
  for i in config['alarms']:
    exec(config['alarms'][i][0])
    config['alarms'][i][1] = compile(config['alarms'][i][1], '<string>', 'exec')
    config['alarms'][i][2] = compile(config['alarms'][i][2], '<string>', 'exec')
    config['alarms'][i][3] = compile(config['alarms'][i][3], '<string>', 'exec')
    config['alarms'][i][4] = compile(config['alarms'][i][4], '<string>', 'exec')
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


  def scanalarms(self,batdata):
    for i in config['alarms']:
      exec(config['alarms'][i][1])
      if self.test:
  #            sys.stderr.write('Alarm 1 triggered')
        exec(config['alarms'][i][2])
      exec(config['alarms'][i][3])
      if self.test:
        exec(config['alarms'][i][4])

  def sendcmd(self,command,replylen):
    """send command/query to Pip4048, return reply"""
    port = serial.Serial(config['files']['pipport'],baudrate=2400)  # open serial port
    port.timeout = 3

    for i in range(5):
      try:
        command=command.encode('ascii','strict')
        crc=self.crccalc(command)
        command=command+crc.to_bytes(2, byteorder='big')+b'\r'
        port.write(command)
        reply = port.read(replylen)
        if  self.crccalc(reply[0:-3]) != int.from_bytes(reply[-3:-1],byteorder='big'):
          raise IOError("CRC error in Pip4048 return string")
          break
      except IOError as err:
        print(err.args)
        if i==4:
          raise
      port.close()
      return reply

  def setparam(self,command,replylen):
    reply=self.sendcmd(command,replylen)
    if reply[1:4]!=b'ACK':
      raise IOError('Bad Parameters')
