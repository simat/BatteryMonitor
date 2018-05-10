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
import time
import serial
import binascii
from config import config
numcells = config['battery']['numcells']
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)

class Pip:
  """Pip4048 inverter coms class"""

  def __init__(self):
    self.floatv='48.0'
    self.bulkv='48.0'
    self.rechargev='48.0'
    self.lowv='44.0'

  def openpip(self,port):
    self.port = serial.Serial(port,baudrate=2400,timeout=1,exclusive=False)  # open serial port

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

    command=command.encode('ascii','strict')
    crc=self.crccalc(command)
    command=command+crc.to_bytes(2, byteorder='big')+b'\r'
    self.port.write(command)
    reply = self.port.read(replylen)
    if  self.crccalc(reply[0:-3]) != int.from_bytes(reply[-3:-1],byteorder='big'):
      raise serial.serialutil.Serial.Exception('CRC error in reply')
    return reply

  def setparam(self,command):
    reply=self.sendcmd(command,7)
    print (command,reply)
    if reply[1:4]!=b'ACK':
      raise IOError('Bad Parameters')

  def stashchargeparams(self):
    """Gets and stashes charging voltage settings from PIP"""
    reply=self.sendcmd('QPIRI',102)
    self.floatv=reply[58:62].decode('ascii','strict')
    self.bulkv=reply[53:57].decode('ascii','strict')
    self.rechargev=reply[43:47].decode('ascii','strict')
    self.lowv=reply[48:52].decode('ascii','strict')

  def setblkflt(self,fltv='48.0',bulkv='48.0'):
    """Sets PIP bulk and float voltage to v and stashes old settings"""
    stashok=False
    for i in range(5):
      try:
        self.openpip(config['files']['pipport'])
        if stashok==False:
          self.stashchargeparams()
        stashok=True
        if bulkv < self.floatv:
          param1='PBFT'+fltv
          param2='PCVV'+bulkv
        else:
          param1='PCVV'+bulkv
          param2='PBFT'+fltv
        print (param1,param2,i)
        self.setparam(param1)
        time.sleep(0.2)
        self.setparam(param2)
        break
      except Exception as err:
        log.error(err)
        time.sleep(0.5)
        if i==4:
          raise
      finally:
        self.port.close()

  def resetblkflt(self):
    """Resets bulk and float voltage back to stashed values"""
    fltv=self.floatv
    bulkv=self.bulkv
    self.setblkflt(fltv,bulkv)

class Rawdat(Pip):

  def __init__(self):
    self.rawdat ={'BInI':0.0,'BOutI':0.0,'BV':0.0,'PVI':0.0,'PVW':0,'ACW':0.0,'ChgStat':00}

  def getdata(self):
    """returns dictionary with data from Pip4048"""
#    log.debug('open')
    for i in range(5):
      try:
        self.openpip(config['files']['pipport'])
        reply=self.sendcmd('QPIGS',110)
        self.rawdat['BInI']=float(reply[47:50].decode('ascii','strict'))
        self.rawdat['BOutI']=float(reply[77:82].decode('ascii','strict'))
        self.rawdat['PVI']=float(reply[60:64].decode('ascii','strict'))
        self.rawdat['BV']=float(reply[41:46].decode('ascii','strict'))
        self.rawdat['ACW']=float(reply[28:32].decode('ascii','strict'))
        reply=self.sendcmd('Q1',74)
  #      log.debug('close')
        self.rawdat['ChgStat']=reply[-5:-3]
        self.rawdat['PVW']=float(reply[53:56].decode('ascii','strict'))
        self.rawdat['ibat']=self.rawdat['BOutI']-self.rawdat['BInI']
        self.rawdat['ipv']=-self.rawdat['PVI']
        self.rawdat['iload']=self.rawdat['ibat']-self.rawdat['ipv']
        break
      except ValueError as err:
        log.error('{}\n{}'.format(err,reply))
        time.sleep(0.5)
        if i==4:
          raise
      except Exception as err:
        log.error(err)
        time.sleep(0.5)
        if i==4:
          raise
      finally:
        self.port.close()


"""class Alarms(Pip):
  # Initialise and compile alarms
  def __init__(self):
    self.overvflg=False
  for i in config['alarms']:
    exec(config['alarms'][i][0])
    config['alarms'][i][1] = compile(config['alarms'][i][1], '<string>', 'exec')
    config['alarms'][i][2] = compile(config['alarms'][i][2], '<string>', 'exec')
    config['alarms'][i][3] = compile(config['alarms'][i][3], '<string>', 'exec')
    config['alarms'][i][4] = compile(config['alarms'][i][4], '<string>', 'exec')

  def scanalarms(self,batdata):
    minvolts = 5.0
    maxvolts = 0.0
    for i in range(1,numcells):
      minvolts = min(batdata.deltav[i],minvolts)
      maxvolts = max(batdata.deltav[i],maxvolts)

    for i in config['alarms']:
      exec(config['alarms'][i][1])
      if self.test:
  #            sys.stderr.write('Alarm 1 triggered')
        exec(config['alarms'][i][2])
      exec(config['alarms'][i][3])
      if self.test:
        exec(config['alarms'][i][4])
        """
