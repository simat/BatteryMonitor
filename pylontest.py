#!/usr/bin/python
# *****BatteryMonitor diagnostic program for Pylontech batteries*****
# Copyright (C) 2021 Simon Richard Matthews
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
from re import match

#commands={'QPIGS':110,'Q':74,'QFLAG':15,'QPIRI':102,'PE':7,'PD':7,'PBCV':7,  \
#          'PCVV':7,'PBFT':7,'PCVT':7}
#commands={}
def openpylon(port):
  openport = serial.Serial(port,baudrate=115200,timeout=1.0)  # open serial port
  return openport

def sendcmd(command,port='/dev/ttyUSB1'):
  """send command/query to Pip4048, return reply"""

#  try:
#    x=match("[A-Z,a-z]*",command)
#    replylen=commands[x.group()]
#  except KeyError:
#    replylen=int(input("Enter Reply Length>"))

  try:
    openport=openpylon(port)
    openport.write(command)
#    reply = openport.read(replylen)
    reply = b''
    for i in range(200):
      char=openport.read(1)
      reply = reply + char
      if char==b'\r':
        break
  except IOError as err:
    print(err.args)
  finally:
    openport.close()

  print (len(reply),reply)
  print(binascii.hexlify(reply))


def setparam(command,port):
  reply=sendcmd(command,port)
  print (reply)
  if reply[1:4]!=b'ACK':
    raise IOError('Bad Parameters')

def getcmd():
  """gets command from user"""
  command=str(input("Enter Command>"))
  return command

def loop():
  while True:
    main()

def main(port='/dev/ttyUSB1'):
    command=getcmd()
    sendcmd(command,port)

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
  """if run from command line, pylontest [command] [port]
  default port /dev/ttyUSB1, if no command ask user"""

  print (sys.argv)
  if len(sys.argv) == 2:
    sendcmd(sys.argv[1])
  else:
    if len(sys.argv) == 3:
      sendcmd(sys.argv[1],sys.argv[2])
    else:
      loop()
