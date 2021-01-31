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
import glob
from config import config
numcells = config['battery']['numcells']
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)

class Bms:
  """Generic Chinese BMS comms class"""

#  def __init__(self,sn):


  def findbms(self):
    """Scan ports to find BMS port"""

    self.bmsport=""
    for dev in glob.glob(config['Ports']['bmsport']):
      for i in range(2):
        try:
          self.openbms(dev)
          reply=self.getbmsdat(self.port,b'\x05\x00')
          if reply.decode('ascii','strict')==self.sn:
            self.bmsport=dev
            break
        except serial.serialutil.SerialException:
          pass
        finally:
          self.port.close()
      if self.bmsport!="":
        break
    if self.bmsport=="":
      raise Exception("Couldn't find BMS hardware name {}".format(self.sn))



  def crccalc(self,data):
    """returns crc as integer from byte stream"""
    crc=0x10000
    for i in data:
      crc=crc-int(i)
    return crc

  def openbms(self,port):
    self.port = serial.Serial(port,timeout=1)  # open serial port

  def getbmsdat(self,port,command):
    """ Issue BMS command and return data as byte data """
    """ assumes data port is open and configured """
    packet=b''
    crc=self.crccalc(command)
    packet=b'\xDD\xA5'+command+crc.to_bytes(2, byteorder='big')+b'\x77'
  #  print (packet)
    data=self.sendbms(self.port,packet)
    return data


  def sendbms(self,port,packet):
        """Send complete command string with crc to BMS"""
    try:
      for i in range(3):
      self.port.flushInput()
      self.port.write(packet)
      reply = self.port.read(4)
  #        raise serial.serialutil.SerialException('hithere')

  #    print (reply)
      x = int.from_bytes(reply[3:5], byteorder = 'big')
  #    print (x)
      data = self.port.read(x)
      end = self.port.read(3)
  #    print (data,end,self.crccalc(reply[2:4]+data),end[0:2])
      if data = b'':
        raise serial.serialutil.SerialException('No Reply')

      if self.crccalc(reply[2:4]+data)!=int.from_bytes(end[0:2],byteorder='big'):
        raise serial.serialutil.SerialException('CRC data= {} calCRC={} CRC={}'.format(data,self.crccalc(reply[2:4]+data),int.from_bytes(end[0:2],byteorder='big')))
  #    print (data)
    except serial.serialutil.SerialException:
      if i=2:
        raise
      else:
        pass

    return data


class Rawdat(Bms):

  def __init__(self,sn):

    self.rawdat={'DataValid':False,'V00':0.0}
    self.sn=sn
    self.findbms()
    """port=self.openbms(config['files']['usbport'])
    data=self.getbmsdat(port,b'\x04\x00') # get BMS voltages
    port.close()
    self.rawdat={'V'+str(x+1):0.0 for x in range(int(len(data)/2))}
    self.rawdat['Ibat']=0.0"""

  def getdata(self):
    self.rawdat['DataValid']=False
    for i in range(5):
      try:
        self.openbms(self.bmsport)
        data=self.getbmsdat(self.port,b'\x04\x00') # get BMS Voltage
#        print(data)
        for i in range(int(len(data)/2)):
          self.rawdat['V{0:0=2}'.format(i+1)]=int.from_bytes(data[i*2:i*2+2], byteorder = 'big')/1000 \
                                              +self.rawdat['V{0:0=2}'.format(i)]
    # convert from cell voltage to total voltages
        data=self.getbmsdat(self.port,b'\x03\x00') # get other BMS data
        self.rawdat['Ibat']=int.from_bytes(data[2:4], byteorder = 'big',signed=True)
        self.rawdat['Bal']=int.from_bytes(data[12:14],byteorder = 'big',signed=False)
        for i in range(int.from_bytes(data[22:23],'big')): # read temperatures
          self.rawdat['T{0:0=1}'.format(i+1)]=(int.from_bytes(data[23+i*2:i*2+25],'big')-2731)/10
#        print (self.rawdat)
        self.rawdat['DataValid']=True
        break
      except ValueError as err:
        log.error('{}\n{}'.format(err,reply))
        time.sleep(1.0)
        if i==4:
          raise
      except Exception as err:
        log.error(err)
        time.sleep(0.5)
        if i==4:
          raise
      finally:
        self.port.close()
