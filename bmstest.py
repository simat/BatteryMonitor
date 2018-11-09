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


configcmd={}
configcmd['FullCap']='dd a5 10 00 ff f0 77'
configcmd['CycleCap']='dd a5 11 00 ff ef 77'
configcmd['?1']='dd a5 12 00 ff ee 77'
configcmd['RateDsg']='dd a5 13 00 ff ed 77'
configcmd['?2']='dd a5 14 00 ff ec 77'
configcmd['?3']='dd a5 15 00 ff eb 77'
configcmd['?4']='dd a5 16 00 ff ea 77'
configcmd['ChgOTPtrig']='dd a5 17 00 ff e9 77'
configcmd['ChgOTPrel']='dd a5 18 00 ff e8 77'
configcmd['ChgUTPtrig']='dd a5 19 00 ff e7 77'
configcmd['ChgUTPrelease']='dd a5 1a 00 ff e6 77'
configcmd['DsgOTPtrig']='dd a5 1b 00 ff e5 77'
configcmd['DsgOTPrelease']='dd a5 1c 00 ff e4 77'
configcmd['DsgUTPtrig']='dd a5 1d 00 ff e3 77'
configcmd['DsgUTPrelease']='dd a5 1e 00 ff e2 77'
configcmd['PackOVPtrig']='dd a5 1f 00 ff e1 77'
configcmd['PackOVPrelease']='dd a5 20 00 ff e0 77'
configcmd['PackUVPtrigger']='dd a5 21 00 ff df 77'
configcmd['PackUVPrelease']='dd a5 22 00 ff de 77'
configcmd['CellOVPtrigger']='dd a5 23 00 ff dd 77'
configcmd['CellOVPrelease']='dd a5 24 00 ff dc 77'
configcmd['CellUVPtrigger']='dd a5 25 00 ff db 77'
configcmd['CellUVPrelease']='dd a5 26 00 ff da 77'
configcmd['ChgOCP']='dd a5 27 00 ff d9 77'
configcmd['DsgOCP']='dd a5 28 00 ff d8 77'
configcmd['?5']='dd a5 29 00 ff d7 77'
configcmd['?6']='dd a5 2a 00 ff d6 77'
configcmd['?7']='dd a5 2b 00 ff d5 77'
configcmd['?8']='dd a5 2c 00 ff d4 77'
configcmd['?9']='dd a5 2d 00 ff d3 77'
configcmd['?10']='dd a5 2e 00 ff d2 77'
configcmd['?11']='dd a5 2f 00 ff d1 77'
configcmd['?12']='dd a5 30 00 ff d0 77'
configcmd['80%Cap']='dd a5 31 00 ff cf 77'
configcmd['60%Cap']='dd a5 32 00 ff ce 77'
configcmd['40%Cap']='dd a5 33 00 ff cd 77'
configcmd['20%Cap']='dd a5 34 00 ff cc 77'
configcmd['HardCellOVP']='dd a5 35 00 ff cb 77'
configcmd['HardCellUVP']='dd a5 36 00 ff ca 77'
configcmd['?13']='dd a5 37 00 ff c9 77'
configcmd['?14']='dd a5 38 00 ff c8 77'
configcmd['?15']='dd a5 39 00 ff c7 77'
configcmd['?16']='dd a5 3a 00 ff c6 77'
configcmd['?17']='dd a5 3b 00 ff c5 77'
configcmd['?18']='dd a5 3c 00 ff c4 77'
configcmd['?19']='dd a5 3d 00 ff c3 77'
configcmd['?20']='dd a5 3e 00 ff c2 77'
configcmd['?21']='dd a5 3f 00 ff c1 77'
configcmd['?22']='dd a5 a0 00 ff 60 77'
configcmd['SN']='dd a5 a1 00 ff 5f 77'
configcmd['Model']='dd a5 a2 00 ff 5e 77'
configcmd['?23']='dd a5 aa 00 ff 56 77'

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
  """ switch charge and discharge fets """
  print ('(0)=Both FETs off')
  print ('(1)=Charge FET on, Discharge FET off')
  print ('(2)=Charge FET off, Discharge FET on')
  print ('(3)=Both FETs on')
  usercmd = input("Enter numeric option> ")
  ser = openbms(port)
  command = bytes.fromhex('DD 5A 00 02 56 78 FF 30 77')
  getbmsdat(ser,command)
  command = bytes.fromhex('DD 5A E1 02 00'+' 0'+usercmd+' 00 FF 1D 77')
  getbmsdat(ser,command)
  command = bytes.fromhex('DD 5A 01 02 00 00 FF FD 77')
  getbmsdat(ser,command)

def getconfig(port='/dev/ttyUSB0'):
  """ Get config settings from BMS"""
  ser = openbms(port)
  command = bytes.fromhex('dd 5a 00 02 56 78 ff 30 77')
  getbmsdat(ser,command)
  for i in configcmd:
    getbmsdat(ser,configcmd[i])
  command = bytes.fromhex('dd 5a 01 02 00 00 ff fd 77')
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
