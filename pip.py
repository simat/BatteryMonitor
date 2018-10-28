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
from config import config
numcells = config['battery']['numcells']
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)

class Rawdat():
  """class for obtaining data from and controlling indidvdual PIP inverters.
  When class is instantiated the SN of the PIP is used to tie the instance of
  the class to the particular machine"""

  def __init__(self,sn):
    self.rawdat ={'DataValid':False,'BInI':0.0,'BOutI':0.0,'BV':0.0,'PVI':0.0,'PVW':0,'ACW':0.0,'ChgStat':00}
    self.pipdown=0.0
    self.sn=sn
    try:
      self.findpip()
    except Exception:
      self.pipdown=time.time() # flag pip is down
    self.stashok=False
    self.floatv=48.0
    self.bulkv=48.0
    self.rechargev=48.0
    self.lowv=44.0
    self.stashok=False


  def findpip(self):
    """Scan ports to find PIP port"""

    self.pipport=""
    for dev in glob.glob(config['Ports']['pipport']):
      for i in range(2):
        try:
          self.openpip(dev)
          reply=self.sendcmd("QID",18)
          if reply[1:15].decode('ascii','strict')==self.sn:
            self.pipport=dev
            break
        except serial.serialutil.SerialException:
          pass
        finally:
          self.port.close
      if self.pipport!="":
        break
    if self.pipport=="":
      raise Exception("Couldn't find PIP sn {}".format(self.sn))

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

    command=command.encode('ascii','strict')
    crc=self.crccalc(command)
    command=command+crc.to_bytes(2, byteorder='big')+b'\r'
    self.port.write(command)
    reply = self.port.read(replylen)
    return reply
    if self.crccalc(reply[0:-3]) != int.from_bytes(reply[-3:-1],byteorder='big'):
      raise serial.serialutil.SerialException('CRC error in reply')

  def setparam(self,command):
    reply=self.sendcmd(command,7)
    print (command,reply)
    if reply[1:4]!=b'ACK':
      raise IOError('Bad Parameters')

  def opensetparam(self,command):
    """open port, send set parameter command to pip, close port"""
    self.openpip(self.pipport)
    self.setparam(command)
    self.port.close

  def stashchargeparams(self):
    """Gets and stashes charging voltage settings from PIP"""
    if self.stashok==False:
      self.stashok=True

  def setblkflt(self,bulkv,floatv):
    if bulkv < self.floatv:
      param1='PBFT'+str(floatv)
      param2='PCVV'+str(bulkv)
    else:
      param1='PCVV'+str(bulkv)
      param2='PBFT'+str(floatv)
    self.setparam(param1)
    time.sleep(0.2)
    self.setparam(param2)

  def setchargevs(self,bulkv=0,floatv=0,lowv=0):
    """Sets PIP charge and discharge limit voltage and stashes old settings
       Only sets non zero voltages """
    self.stashok=False
    reply=self.sendcmd('QPIRI',102)
    self.floatv=reply[58:62].decode('ascii','strict')
    self.bulkv=reply[53:57].decode('ascii','strict')
    self.rechargev=reply[43:47].decode('ascii','strict')
    self.lowv=reply[48:52].decode('ascii','strict')
    for i in range(5):
      try:
        self.openpip(self.pipport)
        self.stashchargeparams()
        if floatv or bulkv:
          self.setblkflt(bulkv,floatv)
        if lowv:
          self.setparam("PSDV"+str(lowv))
        break
      except Exception as err:
        log.error(err)
        time.sleep(0.5)
        if i==4:
          raise
      finally:
        self.port.close()

  def resetchargevs(self,bulkv=0,floatv=0,lowv=0):
    """Resets specified voltages back to stashed values"""
    if bulkv:
      bulkv=self.bulkv
    if floatv:
      floatv=self.floatv
    if lowv:
      lowv=self.lowv
    self.setchargevs(bulkv,floatv,lowv)

  def getdata(self):
    """returns dictionary with data from Pip4048"""
#    log.debug('open')
    if self.pipdown==0.0:
      self.rawdat ={'DataValid':False,'BInI':0.0,'BOutI':0.0,'BV':0.0,'PVI':0.0,'PVW':0,'ACW':0.0,'ChgStat':00}
      for i in range(5):
        try:
          self.openpip(self.pipport)
          reply=self.sendcmd('QPIGS',110)
#          print (reply)
          self.rawdat['BInI']=float(reply[47:50].decode('ascii','strict'))
          self.rawdat['BOutI']=float(reply[77:82].decode('ascii','strict'))
          self.rawdat['PVI']=float(reply[60:64].decode('ascii','strict'))
          self.rawdat['BV']=float(reply[41:46].decode('ascii','strict'))
          self.rawdat['ACW']=float(reply[28:32].decode('ascii','strict'))
          try:
            reply=self.sendcmd('Q1',74)
          except serial.serialutil.SerialException:
#            if reply[-2,-1]!=b'\r': # check for different length reply
            reply=reply+self.port.read(17)
    #      log.debug('close')
          self.rawdat['ChgStat']=reply[69:71]
          self.rawdat['PVW']=float(reply[53:56].decode('ascii','strict'))
          self.rawdat['ibat']=self.rawdat['BOutI']-self.rawdat['BInI']
          self.rawdat['ipv']=-self.rawdat['PVI']
          self.rawdat['iload']=self.rawdat['ibat']-self.rawdat['ipv']
          self.rawdat['DataValid']=True
          break
        except ValueError as err:
          log.error('PIP bad response{}'.format(reply))
          time.sleep(0.5)
          if i==4:
            self.pipdown=time.time() # flag pip is down
            log.error("PIP sn {} interface down".format(self.sn))
        except Exception as err:
          log.error('PIP interface error {}'.format(err))
          time.sleep(0.5)
          if i==4:
            self.pipdown=time.time() # flag pip is down
            log.error("PIP sn {} interface down".format(self.sn))
        finally:
          self.port.close()
    else:
      downtime=time.time()-self.pipdown
      if downtime%600<config['sampling']['sampletime']: #retry interface every 10 minutes
        try:
          self.findpip()
        except:
          pass
#          if downtime>3600: # upgrade error if more than one hour
#            raise
        else:
          self.pipdown=0.0
