import serial
import binascii
# from config import config
# numcells = config['battery']['numcells']
# rawvolts = [ 0 for i in range(numcells+1)]
from config import config
numcells = config['battery']['numcells']

class Raw:
  line1 = [ 0 for i in range(20)]
  rawi = [0.0, 0.0, 0.0]
  rawv = [ 0.0 for i in range(numcells+1)]

  def getbmsdat(self,port,command):
    """ Issue BMS command and return data as byte data """
    """ assumes data port is open and configured """
    port.write(command)
    reply = port.read(4)
  #  print (reply)
    x = int.from_bytes(reply[3:5], byteorder = 'big')
#    print (x)
    data = port.read(x)
    end = port.read(3)
#    print (data)
    return data

  def x(self):
    """ Get data from BMS board"""
    ser = serial.Serial('/dev/ttyUSB0')  # open serial port
    ser.timeout = 3
    command = bytes.fromhex('DD A5 03 00 FF FD 77')
    dat = self.getbmsdat(ser,command)
    self.rawi[0] = int.from_bytes(dat[2:4], byteorder = 'big')
#    print (self.rawi)
#    self.line1 = [ 0 for i in range(int(len(dat)))]
#    for i in range(0,int(len(dat))):
  #    print (dat[i*2:i*2+2])
  #    print (int.from_bytes(dat[i:i+1], byteorder = 'big'))
#      self.line1[i] = int.from_bytes(dat[i:i+1], byteorder = 'big')
#    print (binascii.hexlify(dat))
#    print (self.line1)


  # voltages
    x = 'DD A5 04 00 FF FC 77'
    command = bytes.fromhex('DD A5 04 00 FF FC 77')
    voltages = self.getbmsdat(ser,command)
    for i in range(0,numcells):
      self.rawv[i+1] = int.from_bytes(voltages[i*2:i*2+2], byteorder = 'big')\
                       /1000.00
      self.rawv[i+1] = self.rawv[i+1]+self.rawv[i]
  #  print (self.rawv)
  #  print (binascii.hexlify(voltages))
