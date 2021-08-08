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
from copy import deepcopy
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
initrawdat ={'DataValid':False,'BatI':0.0,'SOC':100.0,\
               'CellV':[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],\
               'Temp':[-50.0,-50.0,-50.0,-50.0,-50.0,-50.0,-50.0,-50.0]}


class Rawdat():
  """class for obtaining data from and controlling indidvdual PIP inverters.
  When class is instantiated the SN of the PIP is used to tie the instance of
  the class to the particular machine"""

  def __init__(self,interfacesinuse):
    self.rawdat = deepcopy(initrawdat)
    self.reply ='' # placeholder for reply from sendcmd
    self.pylondown=0.0
    try:
      self.findpylon()
    except serial.serialutil.SerialException as err:
      self.pylondown=time.time() # flag pylontech is down
      log.error(err)


    self.floatv=48.0
    self.bulkv=48.0
    self.rechargev=48.0
    self.lowv=44.0
#    self.command=b''  # last command sent to pylontech
    self.time=0.0

  def findpylon(self):
    """Scan ports to find pylon port"""

    self.pylonport=""
    for dev in glob.glob(config['Ports']['pylonport']):
      try:
        self.openpylon(dev)
        reply=self.sendcmd('\n')
        # print (reply,dev)
        if b'pylon>' in reply:
          self.pylonport=dev
          break
      except (IOError, serial.serialutil.SerialException):
        pass
      finally:
        self.openport.close
    if self.pylonport=="":
      raise serial.serialutil.SerialException("Couldn't find Pylontech battery")

  def openpylon(self,port):
    self.openport = serial.Serial(port,baudrate=115200,timeout=1)  # open serial port

  def sendcmd(self,command,replylen=2048):
    """send command/query to Pylontech battery, port must be open, return reply"""

    retries=2
    for tries in range(retries):
      try:
        cmd=command.encode('ascii','strict')
        # print ('command ={}'.format(cmd))
        self.openport.write(cmd)
        reply = b''
        starttime=time.time()
        for i in range(replylen):
          char=self.openport.read(1)
          if char==b'': #timeout
            break
          reply = reply + char
#          if char==b'$':
#             if self.openport.read(1)==b'$':
#              break
          if char==b'>':
            break
        if reply:
          break
      except IOError as err:
        print(err.args)
        if tries==retries-1:
          raise
#      print (reply)
    return reply

  batcmdidx ={'Volt':9,'current':18,'temp':27,'SOC':88}
  def getdata(self):
    """returns dictionary with data from Pylontech battery"""
#    log.debug('open')
    # print (initrawdat)
    self.rawdat =deepcopy(initrawdat)
    if self.pylondown==0.0:
      for i in range(5):
        try:
          self.openpylon(self.pylonport)
          cellv=np.empty((8,15), dtype=np.uint16)
          for bat in range(8):
            reply=self.sendcmd('bat {}\n'.format(bat+1))
            reply=reply.decode()
            if 'Invalid command or fail to excute.' in reply:
              numbats=bat
              break
            else:
              idx=reply.index('Coulomb     \r\r\n')+15
              for cell in range(15):
                cellv[bat,cell]=int(reply[idx+9:idx+13])
                self.rawdat['BatI']+=float(reply[idx+14:idx+27])
                self.rawdat['Temp'][bat]=max(self.rawdat['Temp'][bat],float(reply[idx+27:idx+33])/1000)
                self.rawdat['SOC']=min(self.rawdat['SOC'],float(reply[idx+88:idx+91]))
                idx+=110
          self.rawdat['BatI']=self.rawdat['BatI']/(15000)
          cellv.resize(numbats,15)
          # print (cellv)
          maxvs, minvs=np.amax(cellv,axis=0),np.amin(cellv,axis=0)
          maxv,minv=0,5000
          for cell in range(15):
            maxv,minv=max(maxv,maxvs[cell]),min(minv,minvs[cell])
          cellavs=np.median(cellv,axis=0)
          # print (maxvs,maxv,minvs,minv,cellavs)
          #if max or min cell voltage in current cell # store that otherwise average
          for cell in range(15):
            for bat in range(numbats):
              curcell=cellv[bat][cell]
              if curcell==maxv or curcell==minv:
                self.rawdat['CellV'][cell]+=float(curcell)/1000.0
                if cell < 15-1:
                  self.rawdat['CellV'][cell+1]=self.rawdat['CellV'][cell]
                break
              elif bat==numbats-1:
                self.rawdat['CellV'][cell]+=int(cellavs[cell])/1000.0
                if cell < 15-1:
                  self.rawdat['CellV'][cell+1]=self.rawdat['CellV'][cell]
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
          self.openport.close()
          print (self.rawdat)
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
