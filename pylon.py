# *****BatteryMonitor pylontech battery driver*****
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
import numpy as np
import sys
import time
import serial
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
    self.rawdat = dict.copy(initrawdat)
    self.reply ='' # placeholder for reply from sendcmd
    self.pythondown=0.0
    self.sn=sn
    try:
      self.findpython()
    except serial.serialutil.SerialException as err:
      self.pythondown=time.time() # flag pylontech is down
      log.error(err)


    self.floatv=48.0
    self.bulkv=48.0
    self.rechargev=48.0
    self.lowv=44.0
    self.command=b''  # last command sent to pylontech
    self.time=0.0

  def findpylon(self):
    """Scan ports to find pylon port"""

    self.pylonport=""
    for dev in glob.glob(config['Ports']['pylonport']):
      try:
        self.openpylon(dev)
      except IOError:
        pass
      else:
          self.sendcmd('\r\n')
          self.reply=self.reply.decode()
          if 'pylon>' in self.reply:
            break
          else:
            raise serial.serialutil.SerialException('No pylon> prompt'):
      self.sendcmp('info')  # get Pylontech info
      if self.sn in reply:
        self.pylonport=dev
        break
      except serial.serialutil.SerialException:
        pass
      finally:
        self.port.close
    if self.pylonport!="":
      break
    else:
      raise serial.serialutil.SerialException("Couldn't find PIP sn {}".format(self.sn))

  def openpylon(self,port):
    self.openport = serial.Serial(port,baudrate=115200,timeout=1)  # open serial port

  def sendcmd(command,replylen=2048):
    """send command/query to Pylontech battery, port must be open, return reply"""

    retries=2
    for tries in range(retries):
      try:
        cmd=command.encode('ascii','strict')
        self.openport.write(cmd)
        reply = b''
        starttime=time.time()
        for i in range(replylen):
          char=self.openport.read(1)
          if char=='': #timeout
            raise serial.serialutil.SerialException('No reply from Pylontech')
          reply = reply + char
          if char==b'$':
            if openport.read(1)==b'$':
              break
          elif char==b'>'
            break
      except IOError as err:
        print(err.args)
        if tries==retries-1:
          raise

initrawdat ={'DataValid':False,'BatI':0.0,\
             'CellV':[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],\
             'Temp':[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]}
batcmdidx ={'Volt':9,'current':18,'temp':27,'SOC':88}
  def getdata(self):
    """returns dictionary with data from Pylontech battery"""
#    log.debug('open')
    self.rawdat = dict.copy(initrawdat)
    if self.pylondown==0.0:
      for i in range(5):
        try:
          self.openpylon(self.pylonport)
          cellv=np.empty((8,15))
          for bat in range(8):
            self.sendcmd('bat {}'.format(bat))
            self.reply=self.reply.decode()
            if 'Invalid command or fail to excute.' in self.reply:
              numbats=bats+1
              break
            else:
              idx=self.reply.index('Coulomb     \r\r\n')+8
              x=idx+batcmdidx['current']
              self.rawdat['BatI']=float(self.reply[x:x+4])
              x=idx+batcmdidx['SOC']
              self.rawdat['SOC']=int(self.reply[x:x+3])
              for cell in range(15):
                x=idx+batcmdidx['Volt']
                cellv[bat][cell]=float(self.reply[x:x+4])/1000

          cellv.resize(numbats,15)
          maxv, minv=np.amax(cellv,axis=0),np.amin(cellv,axis=0)
          cellav=np.median(cellv,axis=0)
          #if max or min cell voltage in current cell # store that otherwise average
          for cell in range(15):
            for bat in range(numbats):
              curcell=cellv[cell][bat]
              if curcell==maxv or curcell==minv:
                self.rawdat['CellV'][cell]=curcell
                break
            if self.rawdat['CellV'][cell]==0:
              self.rawdat['CellV'][cell]=cellav[cell]

          self.rawdat['DataValid']=True
          break
        except ValueError as err:
          log.error('Pylon bad response{} to command {}'.format(self.reply,self.command))
          time.sleep(0.5)
          if i==4:
            self.pylondown=time.time() # flag pylon is down
            log.error("Pylon interface down")
        except serial.serialutil.SerialException as err:
          log.error('PIP interface error {}'.format(err))
          time.sleep(0.5)
          if i==4:
            self.pylondown=time.time() # flag pylon is down
            log.error("Pylon interface down")
        finally:
          self.port.close()
    else:
      downtime=time.time()-self.pylondown
      if downtime!=0 and downtime%600<config['sampling']['sampletime']: #retry interface every 10 minutes
        try:
          self.findpylon()
        except serial.serialutil.SerialException:
          pass
#          if downtime>3600: # upgrade error if more than one hour
#            raise
        else:
          self.pylondown=0.0
          log.info("PIP sn {} interface back up".format(self.sn))
