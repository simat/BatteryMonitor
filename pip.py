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
import glob
from threading import Thread
from config import config
numcells = config['battery']['numcells']
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)
initrawdat ={'DataValid':False,'BInI':0.0,'BOutI':0.0,'BV':0.0,'PVI':0.0,'PVW':0,'ACW':0.0,'ACV':0.0,'ChgStat':b'00'}



class Rawdat():
  """class for obtaining data from and controlling indidvdual PIP inverters.
  When class is instantiated the SN of the PIP is used to tie the instance of
  the class to the particular machine"""

  def __init__(self,sn,InterfacesInUse):
    self.rawdat = dict.copy(initrawdat)
    self.reply ='' # placeholder for reply from sendcmd
    self.pipdown=0.0
    self.sn=sn
    self.timeslaveon=0  # time slave inverter was turned on
    try:
      self.findpip(InterfacesInUse)
    except IOError as err:
      self.pipdown=time.time() # flag pip is down
      log.error(err)


    self.stashok=False
    self.floatv=48.0
    self.bulkv=48.0
    self.rechargev=48.0
    self.lowv=44.0
    self.stashok=False
    self.command=b''  # last command sent to PIP
    self.acloadav=0.0
    self.timeoverload=0.0  #time overload started
    self.time=0.0

  def findpip(self,InterfacesInUse):
    """Scan ports to find PIP port"""

    self.pipport=""
    for dev in glob.glob(config['Ports']['pipport']):
      if dev not in InterfacesInUse:
#        print(dev)
        for i in range(2):
          try:
            self.openpip(dev)
            self.sendcmd("QID",18)
            if self.reply[1:15].decode('ascii','strict')==str(self.sn):
              self.pipport=dev
              break
          except IOError:
            pass
          finally:
            self.port.close
        if self.pipport!="":
          break
    if self.pipport=="":
      raise IOError("Couldn't find PIP sn {}".format(self.sn))

  def openpip(self,port):
    self.port = serial.Serial(port,baudrate=2400,timeout=1)  # open serial port

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
    self.command=command.encode('ascii','strict')
    crc=self.crccalc(self.command)
    self.command=self.command+crc.to_bytes(2, byteorder='big')+b'\r'
    self.port.reset_input_buffer()
    self.port.write(self.command)
    for i in range(1000):
      self.reply=self.port.read(1)
#      print (self.reply)
      if self.reply!=b'\r' and self.reply!=b'(':
        break
    self.reply = b'('+self.reply+self.port.read(replylen-2)
#    print('command {} reply {}'.format(self.command,self.reply))
    if self.crccalc(self.reply[0:-3]) != int.from_bytes(self.reply[-3:-1],byteorder='big'):
      raise IOError('CRC error in reply')

  def sendQ1(self):  #special to send Q1 command due to variable length reply
    try:
      self.sendcmd('Q1',74)
    except IOError:
      if self.reply[-2:-1]!=b'\r': # check for different length self.reply
        self.reply=self.reply+self.port.read(17)

  def setparam(self,command):
#    time.sleep(5.0)
    self.sendcmd(command,7)
    if self.reply[1:4]!=b'ACK':
#      raise IOError('Bad Parameters')
       log.error('Bad Reply {} to command {}'.format(self.reply,command))


  def opensetparam(self,command):
    """open port, send set parameter command to pip, close port"""
    self.openpip(self.pipport)
    self.setparam(command)
    self.port.close

  def setparamnoerror(self,command): # set parameter, ignore errors
    try:
      self.opensetparam(command)
    except IOError:
      pass

  def backgroundswapinv(self):
    """Turns slave pip inverter on, waits for powerup and them turns
       master pip inverter off"""

    try:
      self.opensetparam('MNCHGC1498')
    except IOError:
      pass
    else:
      time.sleep(20) # wait for second inverter to power up and syncronise
      try:
        self.opensetparam('MNCHGC0497')
      except IOError:
        pass

  def swapinverter(self):
    """turns on inverter controlled by Pi pin number if on arg and turns off
       inverter controlled by Pi pin number in off arg"""

    if self.timeoverload==0: # only swap inverters if no overload
      Thread(target=self.backgroundswapinv).start()

  def slaveinvon(self):
    """turns on slave inverter, set overload timer, timer set to zero when
       power draw less than 60% of inverter load for half an hour"""

    self.timeoverload=time.time()
    try:
      self.opensetparam('MNCHGC1498')  # turn on slave
    except IOError:
      pass

  def slaveinvoff(self):
    """turn slave inverter off"""
    try:
      self.opensetparam('MNCHGC1497')  # turn off slave
    except IOError:
      pass


  def getdata(self):
    """returns dictionary with data from Pip4048"""
#    log.debug('open')
    self.rawdat = dict.copy(initrawdat)
    if self.pipdown==0.0:
      for i in range(5):
        try:
          self.openpip(self.pipport)
          self.sendcmd('QPIGS',110)
          self.rawdat['BInI']=float(self.reply[47:50].decode('ascii','strict'))
          self.rawdat['BOutI']=float(self.reply[77:82].decode('ascii','strict'))
          self.rawdat['PVI']=float(self.reply[60:64].decode('ascii','strict'))
          self.rawdat['BV']=float(self.reply[41:46].decode('ascii','strict'))
          self.rawdat['ACW']=float(self.reply[28:32].decode('ascii','strict'))
          self.rawdat['ACV']=float(self.reply[11:16].decode('ascii','strict'))
          self.sendQ1()
          self.rawdat['ChgStat']=self.reply[69:71]
          self.rawdat['PVW']=float(self.reply[53:56].decode('ascii','strict'))*10
          self.rawdat['ibat']=self.rawdat['BOutI']-self.rawdat['BInI']
          self.rawdat['ipv']=self.rawdat['PVW']/self.rawdat['BV']
          self.rawdat['iload']=-self.rawdat['ACW']/self.rawdat['BV']
          self.rawdat['DataValid']=True
          print (self.rawdat)
          break
        except ValueError as err:
          log.error('PIP bad response{} to command {}'.format(self.reply,self.command))
          time.sleep(0.5)
          if i==4:
            self.pipdown=time.time() # flag pip is down
            log.error("PIP sn {} interface down".format(self.sn))
        except IOError as err:
          log.error('PIP interface error {}'.format(err))
          time.sleep(0.5)
          if i==4:
            self.pipdown=time.time() # flag pip is down
            log.error("PIP sn {} interface down".format(self.sn))
        finally:
          self.port.close()
    else:
      missedsamples=(time.time()-self.pipdown)//config['sampling']['sampletime']
      if missedsamples%(600/config['sampling']['sampletime'])==0:  #retry interface every 10 minutes
        try:
          self.findpip([])
        except IOError:
          pass
#          if downtime>3600: # upgrade error if more than one hour
#            raise
        else:
          self.pipdown=0.0
          log.info("PIP sn {} interface back up".format(self.sn))

    self.acloadav = (self.acloadav*2 + self.rawdat['ACW'])/3  # running average
#    print ('acloadav {} ACW1 {} '.format(self.acloadav,self.rawdat['ACW']))
    if self.timeoverload !=0.0:
      self.time=time.time()
      if self.acloadav*config['Inverters']['numinverters']>config['Inverters']['turnonslave']  \
         or self.rawdat['ACW']*config['Inverters']['numinverters']>config['Inverters']['turnonslave']*1.3:
        self.timeoverload=self.time
      if self.time-self.timeoverload > config['Inverters']['minruntime']:
        self.timeoverload =0.0
