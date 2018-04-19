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

import sys
import serial
import binascii

commands={'QPIGS':110,'Q1':74,'QFLAG':15,'QPIRI':102,'PEj':7,'PDj':7}
#commands={}
def openpip(port):
  openport = serial.Serial(port,baudrate=2400,timeout=1.0,exclusive='True')  # open serial port
  return openport

def sendcmd(command,openport,replylen):
  """send command/query to Pip4048, return reply"""

  for i in range(5):
    try:
      command=command.encode('ascii','strict')
      crc=crccalc(command)
      command=command+crc.to_bytes(2, byteorder='big')+b'\r'
      openport.write(command)
      reply = openport.read(replylen)
#      if  crccalc(reply[0:-3]) != int.from_bytes(reply[-3:-1],byteorder='big'):
#        raise IOError("CRC error in Pip4048 return string")
      break
    except IOError as err:
      print(err.args)
      if i==4:
        raise
  return reply

def setparam(command,port):
  reply=sendcmd(command,port)
  print (reply)
  if reply[1:4]!=b'ACK':
    raise IOError('Bad Parameters')

def getcmd(port):
  """gets command from user"""
  command=str(input("Enter Command>"))
  try:
    replylen=commands[command]
  except KeyError:
    replylen=int(input("Enter Reply Length>"))

  openport=openpip(port)
  reply=sendcmd(command,openport,replylen)
  openport.close()
  print (len(reply),reply)
  print(binascii.hexlify(reply))
  if command=='QPIGS':
    print ('AC output V =',reply[12:17])
    print ('AC output VA =',reply[23:27])
    print ('AC output W =',reply[28:32])
    print ('Bus V =',reply[37:40])
    print ('Battery V =',reply[41:46])
    print ('Battery In I =',reply[47:50])
    print ('Heat sink T =',reply[51:54])
    print ('PV Input current for battery I =',reply[60:64])
    print ('PV Input V =',reply[65:70])
    print ('Battery V from SCC =',reply[71:76])
    print ('Battery Discharge I =',reply[77:82])
    print ('Status =',reply[83:91])



def main(port='/dev/ttyUSB1'):
  while True:
    getcmd(port)


def crccalc(command):
  """returns crc as integer from binary string command"""

  crc=binascii.crc_hqx(command,0)
  crchi=crc>>8
  crclo=crc&255

  if crchi == 0x28 or crchi==0x0d or crchi==0x0a:
    crc+=256

  if crclo == 0x28 or crclo==0x0d or crclo==0x0a:
    crc+=1
  return crc

if __name__ == "__main__":
  main()
