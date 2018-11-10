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
configcmd['FullCap']=b'\x10'
configcmd['CycleCap']=b'\x11'
configcmd['?1']=b'\x12'
configcmd['RateDsg']=b'\x13'
configcmd['?2']=b'\x14'
configcmd['?3']=b'\x15'
configcmd['?4']=b'\x16'
configcmd['ChgOTPtrig']=b'\x17'
configcmd['ChgOTPrel']=b'\x18'
configcmd['ChgUTPtrig']=b'\x19'
configcmd['ChgUTPrelease']=b'\x1a'
configcmd['DsgOTPtrig']=b'\x1b'
configcmd['DsgOTPrelease']=b'\x1c'
configcmd['DsgUTPtrig']=b'\x1d'
configcmd['DsgUTPrelease']=b'\x1e'
configcmd['PackOVPtrig']=b'\x1f'
configcmd['PackOVPrelease']=b'\x20'
configcmd['PackUVPtrigger']=b'\x21'
configcmd['PackUVPrelease']=b'\x22'
configcmd['CellOVPtrigger']=b'\x23'
configcmd['CellOVPrelease']=b'\x24'
configcmd['CellUVPtrigger']=b'\x25'
configcmd['CellUVPrelease']=b'\x26'
configcmd['ChgOCP']=b'\x27'
configcmd['DsgOCP']=b'\x28'
configcmd['?5']=b'\x29'
configcmd['?6']=b'\x2a'
configcmd['?7']=b'\x2b'
configcmd['?8']=b'\x2c'
configcmd['?9']=b'\x2d'
configcmd['?10']=b'\x2e'
configcmd['?11']=b'\x2f'
configcmd['?12']=b'\x30'
configcmd['80%Cap']=b'\x31'
configcmd['60%Cap']=b'\x32'
configcmd['40%Cap']=b'\x33'
configcmd['20%Cap']=b'\x34'
configcmd['HardCellOVP']=b'\x35'
configcmd['HardCellUVP']=b'\x36'
configcmd['?13']=b'\x37'
configcmd['?14']=b'\x38'
configcmd['?15']=b'\x39'
configcmd['?16']=b'\x3a'
configcmd['?17']=b'\x3b'
configcmd['?18']=b'\x3c'
configcmd['?19']=b'\x3d'
configcmd['?20']=b'\x3e'
configcmd['?21']=b'\x3f'
configcmd['?22']=b'\xa0'
configcmd['SN']=b'\xa1'
configcmd['Model']=b'\xa2'
configcmd['?23']=b'\xaa'

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
  configitem=input("Enter config item>")
  configitem=configcmd[configitem]
#  print ('register=',configitem)
  rw=input("r or w>")
  if rw=='w':
    rw=b'\x5a'
    configdata=int(input('Enter data>'))
    configitem=configitem+b'\x02'+configdata.to_bytes(2, byteorder='big')
#    print ('value=',configdata,configitem)
  else:
    rw=b'\xa5'
    configitem=configitem+b'\x00'
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
#  for i in configcmd:
#  print('rw=',rw,'command=',configitem)
  packet=b'\xDD'+rw+configitem+crccalc(configitem).to_bytes(2, byteorder='big')+b'\x77'
  print ('register command=',binascii.hexlify(packet))
  data=getbmsdat(ser,packet)
  print ('register reply=',binascii.hexlify(data),int.from_bytes(data, byteorder = 'big'))
  command = bytes.fromhex('dd 5a 01 02 00 00 ff fd 77')
  print ('command=',binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))

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

def crccalc(data):
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
      loop()
