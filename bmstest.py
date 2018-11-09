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
configcmd['FullCap']='10 00'
configcmd['CycleCap']='11 00'
configcmd['?1']='12 00
configcmd['RateDsg']='13 00'
configcmd['?2']='14 00'
configcmd['?3']='15 00'
configcmd['?4']='16 00'
configcmd['ChgOTPtrig']='17 00'
configcmd['ChgOTPrel']='18 00'
configcmd['ChgUTPtrig']='19 00'
configcmd['ChgUTPrelease']='1a 00'
configcmd['DsgOTPtrig']='1b 00'
configcmd['DsgOTPrelease']='1c 00'
configcmd['DsgUTPtrig']='1d 00'
configcmd['DsgUTPrelease']='1e 00'
configcmd['PackOVPtrig']='1f 00'
configcmd['PackOVPrelease']='20 00'
configcmd['PackUVPtrigger']='21 00'
configcmd['PackUVPrelease']='22 00'
configcmd['CellOVPtrigger']='23 00'
configcmd['CellOVPrelease']='24 00'
configcmd['CellUVPtrigger']='25 00'
configcmd['CellUVPrelease']='26 00'
configcmd['ChgOCP']='27 00'
configcmd['DsgOCP']='28 00'
configcmd['?5']='29 00'
configcmd['?6']='2a 00'
configcmd['?7']='2b 00'
configcmd['?8']='2c 00'
configcmd['?9']='2d 00'
configcmd['?10']='2e 00'
configcmd['?11']='2f 00'
configcmd['?12']='30 00'
configcmd['80%Cap']='31 00'
configcmd['60%Cap']='32 00'
configcmd['40%Cap']='33 00'
configcmd['20%Cap']='34 00'
configcmd['HardCellOVP']='35 00'
configcmd['HardCellUVP']='36 00'
configcmd['?13']='37 00'
configcmd['?14']='38 00'
configcmd['?15']='39 00'
configcmd['?16']='3a 00'
configcmd['?17']='3b 00'
configcmd['?18']='3c 00'
configcmd['?19']='3d 00'
configcmd['?20']='3e 00'
configcmd['?21']='3f 00'
configcmd['?22']='a0 00'
configcmd['SN']='a1 00'
configcmd['Model']='a2 00'
configcmd['?23']='aa 00'

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
  configitem=bytes.fromhex(configcmd[configitem])
  r/w=input("r or w>")
  if r/w='w':
    r/w=b'\x5a'
    configdata=('Enter data>')
    configitem=configitem+configdata.to_bytes(2, byteorder='big')
  else:
    r/w=b'\xa5'
  ser = openbms(port)
  command = bytes.fromhex('DD A5 03 00 FF FD 77')
  print (binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print (binascii.hexlify(data))
  command = bytes.fromhex('DD A5 04 00 FF FC 77')
  print (binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print (binascii.hexlify(data))
  command = bytes.fromhex('dd 5a 00 02 56 78 ff 30 77')
  print (binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print (binascii.hexlify(data))
#  for i in configcmd:
  print (configcmd[configitem])
  packet=b'\xDD'+r/w+configitem+crc.to_bytes(2, byteorder='big')+b'\x77'
  data=getbmsdat(ser,packet)
  print (configitem,binascii.hexlify(data),int.from_bytes(data, byteorder = 'big'))
  command = bytes.fromhex('dd 5a 01 02 00 00 ff fd 77')
  print (binascii.hexlify(command))
  data=getbmsdat(ser,command)
  print (binascii.hexlify(data))

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
      loop()
