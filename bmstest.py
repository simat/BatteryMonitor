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
  print ('(01)=Discharge FET on, Charge FET off')
  print ('(02)=Discharge FET off, Charge FET on')
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
  data=bmscore.getbmsdat(ser,command)
  print ('reply=',binascii.hexlify(data))
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
  dat = bmscore.getbmsdat(ser,command)
  rawi = int.from_bytes(dat[2:4], byteorder = 'big',signed=True)
  rawv = int.from_bytes(dat[0:2], byteorder = 'big',signed=True)
  balance = int.from_bytes(dat[12:14], byteorder = 'big',signed=True)
  state = int.from_bytes(dat[16:18], byteorder = 'big',signed=True)
  fets = int.from_bytes(dat[20:21], byteorder = 'big',signed=True)
  print ("V={} I={} bal={} state={} fets={}".format(rawv,rawi,balance,state,fets))
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
#    rawv[i] = rawv[i]+rawv[i-1]
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

def findregname(reg):
  """Find register name given register address"""

  regname=None
  for i in bmscore.configinmem:
    if bmscore.configinmem[i]['reg']==reg:
      regname=i
      break
  return regname

def enterreg():
  """Changes individual register in memory"""

  cmd=int(input('By Name (1) or by register number (2)?>'))
  if cmd==1:
    item=input("Enter Config Item Name>")
  elif cmd==2:
    item=str.upper(input("Enter Config Register Address>"))
    item=findregname(item)
    value=input("{} = {}, Enter New Value, [return] for don't write>" \
        .format(item,bmscore.configinmem[item]['value']))
  valueascii=" "+value
  reginfo ={}
  if value:
    try:
      valueint=int(value)
    except ValueError:
      valueint=None
    reginfo={item:{"valueint":valueint,"valueascii":valueascii}}
  return reginfo

def chgreg(reginfo):
  """Stores Values in reginfo dictionary"""
  for reg in reginfo:
    valueint=reginfo[reg]['valueint']
    valueascii=reginfo[reg]['valueascii']
    bmscore.configinmem[reg]['value']=eval(bmscore.configinmem[reg]['decode'])

def main():
  print (sys.argv)
  if len(sys.argv) == 2:
    sendcmd(sys.argv[1])
  elif len(sys.argv) == 3:
    sendcmd(sys.argv[1],sys.argv[2])
  elif len(sys.argv) == 1:

    print ('Enter BMS port address option [3]')
    print ('(1) /dev/ttyUSB0')
    print ('(2) /dev/ttyUSB1')
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
      print('(1) Load all config data from BMS to memory')
      print('(2) Read all config data from disk to memory')
      print('(3) Write all config data from memory to BMS')
      print('(4) Write all config data from memory to disk')
      print('(5) Dump all config data in memory')
      print('(6) Dump raw config data in memory')
      print('(7) Read/Write config item in memory')
      print('(8) Read/Write single register in memory and on BMS PCB')
      print('(9) Read BMS data')
      print('(10) Switch charge/discharge FETs')
      print('(11) Calibrate BMS')
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
        count = 0
        for i in bmscore.configinmem:
          print ('{}={}{} {}'.format \
          (i,bmscore.configinmem[i]['value'],bmscore.configinmem[i]['units'],bmscore.configinmem[i]['comment']))
          count=count+1
          if count%30==0:
            x=input("press return for next page")

      elif cmd==7:
        reg=enterreg()
        chgreg(reg)
      elif cmd==6:
        count=0
        for i in bmscore.configinmem:
          print (i,bmscore.configinmem[i])
          count=count+1
          if count%30==0:
            x=input("press return for next page")
      elif cmd==8:
        reg=enterreg()
        chgreg(reg)
        if reg!={}:
          reglist=[]
          reglist.append(*reg)
          bmscore.configitems(reg,port,write=True)
      elif cmd==9:
        getdat(port)
      elif cmd ==10:
        switchfets(port)
      elif cmd ==11:
        print ('Enter Item to Calibrate?')
        print ('(1) Cell Voltages')
        print ('(2) Idle Current')
        print ('(3) Charge Current')
        print ('(4) Discharge Current')
        item=int(getcmd())
        if item==1:
          print ()
          item=input("Enter cell number/s e.g. '1-4,5'?> ")
          result=set()
          for part in item.split(','):
            x=part.split('-')
            result.update(range(int(x[0]),int(x[-1])+1))
          celllist=sorted(result)
          cellvolts=int(input("Enter cell voltage/s in mV?> "))
          reglist={}
          for i in range(len(celllist)):
            reg=findregname(str.upper(format(celllist[i]+0xAF,'02x')))
            reglist[reg]={'valueint':cellvolts,'valueascii':None}
          chgreg(reglist)
          bmscore.configitems(reglist,port,write=True)

        elif port == 2:
          port='/dev/ttyUSB1'
        else:
          port=str(input("Enter port name>"))


if __name__ == "__main__":
  """if run from command line"""
  main()
