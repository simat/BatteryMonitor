#!/usr/bin/python
# *****Program to retrieve and store data to BMS PCBs*****
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

import bmscore
import sys
import binascii

def getcmd():
  """gets command from user"""
  command=str(input("Enter Command>"))
  return command

def switchfets(port='/dev/ttyUSB0'):
  """ switch charge and discharge fets """
  print ('(03)=Both FETs off')
  print ('(01)=Charge FET on, Discharge FET off')
  print ('(02)=Charge FET off, Discharge FET on')
  print ('(00)=Both FETs on')
  usercmd = input("Enter numeric option> ")
  ser = bmscore.openbms(port)
  command = bytes.fromhex('DD A5 03 00 FF FD 77')
  print ('command=',binascii.hexlify(command))
  data=bmscore.getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))
  command = bytes.fromhex('DD A5 04 00 FF FC 77')
  print ('command=',binascii.hexlify(command))
  data=bmscore.getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))
  command = bytes.fromhex('DD 5A 00 02 56 78 FF 30 77')
  getbmsdat(ser,command)
  usercmd=b'\xE1\x02\x00'+bytes.fromhex(usercmd)
  command = b'\xDD\x5A'+usercmd+bmscore.crccalc(usercmd).to_bytes(2, byteorder='big')+b'\x77'
  print (binascii.hexlify(command))
  bmscore.getbmsdat(ser,command)
  command = bytes.fromhex('DD 5A 01 02 00 00 FF FD 77')
  bmscore.getbmsdat(ser,command)

def getdat(port='/dev/ttyUSB0'):
  """ Get data from BMS board"""
  ser = bmscore.openbms(port)
  command = bytes.fromhex('DD A5 03 00 FF FD 77')
  dat = bmscore.getbmsdat(ser,command)
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
  voltages = bmscore.getbmsdat(ser,command)
  ser.close
  print (binascii.hexlify(voltages))
  rawv = [ 0.0 for i in range(15)]
  for i in range(15):
    rawv[i] = int.from_bytes(voltages[i*2:i*2+2], byteorder = 'big')/1000.00
    rawv[i] = rawv[i]+rawv[i-1]
  print (rawv)

  command = bytes.fromhex('DD A5 05 00 FF FB 77')
  dat = bmscore.getbmsdat(ser,command)

#  line1 = [ 0 for i in range(int(len(dat)))]
#  for i in range(0,int(len(dat))):
#    print (dat[i*2:i*2+2])
#    print (int.from_bytes(dat[i:i+1], byteorder = 'big'))
#    line1[i] = int.from_bytes(dat[i:i+1], byteorder = 'big')
  print (binascii.hexlify(dat))
#  print (line1)

def main():
  print (sys.argv)
  if len(sys.argv) == 2:
    sendcmd(sys.argv[1])
  elif len(sys.argv) == 3:
    sendcmd(sys.argv[1],sys.argv[2])
  elif len(sys.argv) == 1:

    print ('Enter BMS port address option [3]')
    print ('(1) /ttyUSB0')
    print ('(2) /ttyUSB1')
    print ('(3) other')
    port=int(getcmd())
    if port==1:
      port='/dev/ttyUSB0'
    elif port == 2:
      port='/dev/ttyUSB1'
    else:
      port=str(input("Enter port name>"))

    while True:
      bmscore.openbms(port)

      print('Enter option')
      print('(1) Load config data from BMS PCB')
      print('(2) Read config data from disk')
      print('(3) Write config data to BMS PCB')
      print('(4) Write config data to disk')
      print('(5) Dump config data')
      print('(6) Change config item by name')
      print('(7) Change config item by register address')
      print('(8) Dump raw config data')

      cmd=int(getcmd())
      if cmd==1:
        bmscore.configitems(bmscore.fullconfiglist,port)
      elif cmd==2:
        file=str(input("Enter filename>"))
        bmscore.configinmem=bmscore.rdjson(file)
      elif cmd==3:
        bmscore.configitems(bmscore.fullconfiglist,port,write=True)
      elif cmd==4:
        file=str(input("Enter filename>"))
        bmscore.wrjson(file,bmscore.configinmem)
      elif cmd ==5:
        for i in bmscore.configinmem:
          print ('{}={}{}'.format(i,bmscore.configinmem[i]['value'],bmscore.configinmem[i]['units']))
      elif cmd==6:
        item=input("Enter Config Item Name>")
        value=input('{} = {}, Enter New Value>'.format(item,bmscore.configinmem[item]['value']))
        bmscore.configinmem[item]['value']=eval(bmscore.configinmem[item]['decode'])
        print (bmscore.configinmem[item]['value'])
      elif cmd==7:
        reg=input("Enter Config Register Address>")
        for i in bmscore.configmem:
          if bmscore.configinmem[i]['reg']==item:
            item=i
            break

        value=input('Register {} = {}, Enter New Value>'.format(item,bmscore.configinmem[item]['value']))
        bmscore.configinmem[item]['value']=value
      elif cmd==8:
        for i in bmscore.configinmem:
          print (i,bmscore.configinmem[i])

if __name__ == "__main__":
  """if run from command line, piptest [command] [port]
  default port /dev/ttyUSB1, if no command ask user"""
  main()
