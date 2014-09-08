#!/usr/bin/python
import sys
import time
#import smbus
#from Adafruit_I2C import Adafruit_I2C
import ADS1x15 as AtoD
import ast

AtoD0 = AtoD.ADS1x15(ic=0x01, debug=True)
AtoD1 = AtoD.ADS1x15(address=0x49,ic=0x01, debug=True)
AtoD2 = AtoD.ADS1x15(address=0x4A,ic=0x01, debug=True)
voltages = [0, 3.25, 6.5, 9.75, 13.00, 16.25, 19.50, 22.75, 26.00]
deltav = [0, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25]
rawvolts = voltages
rawcurrent = 0.0
current = 0.0
# calvolts = [3.289/3.298, 6.593/6.598, 9.880/9.901, 13.158/13.204, 16.465/16.509, 19.768/19.817, 23.052/23.08, 26.369/26.38] 
calvolts = [1, 1, 1, 1, 1, 1, 1, 1]
# real = [-0.016, 3.333, 6.671, 10.012, 13.354, 16.697, 20.044, 23.35, 26.69]
# measured = [-0.016, 3.329, 6.677, 10.007, 13.328, 16.68, 20.023, 23.349, 26.705, -10.5, 220.1]

# real = [-.017, 3.327, 6.658, 9.990, 13.322, 16.657, 19.992, 23.28, 26.61]
# measured = [-0.017, 3.319, 6.652, 9.968, 13.276, 16.612, 19.943, 23.249, 26.591, 1.0, 220.2]
real = [-0.017, 3.327, 3.327, 3.327, 3.327, 3.328, 3.329, 3.328, 3.328]
measured =[-0.017, 3.320, 3.335, 3.317, 3.308, 3.337, 3.331, 3.308, 3.343, 1.0, 220.2]
calvolts = [real[i] - measured[i] for i in range (1,9)]

class summaryClass:
  """Handles battery summary data""" 

#  hivolts = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#  lowvolts = [ 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]


  def __init__(self):
    try:
      self.summaryfile = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/summary','r+')
      self.data = ast.literal_eval(self.summaryfile.read())
    except IOError:
      print ('file error')
#      summary = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/summary','w')
#      pickle.dump(hivolts, summary)
#      pickle.dump(lowvolts, summary)
#      summary.close()

  def write(self):
    self.summaryfile.seek(0)
    self.summaryfile.write(str(self.data))

  def close(self):
    self.write()
    self.summaryfile.close()

def getraw():
  deamon.rawvolts = [AtoD2.readADCSingleEnded(channel=2, pga=2048, sps=250)/1000] # 0 volts
  deamon.rawvolts = deamon.rawvolts + [AtoD0.readADCSingleEnded(channel=n, pga=2048, sps=250)/1000 for n in range(4)] # battery 1 to 4 in volts
  deamon.rawvolts = deamon.rawvolts + [AtoD1.readADCSingleEnded(channel=n, pga=2048, sps=250)/1000 for n in range(4)] # battery 5 to 8 in volts
  deamon.rawcurrent = AtoD2.readADCDifferential(chP=0, chN=1, pga=256, sps=250) # Battery current in counts

summary = summaryClass()
def deamon(soc=0):
  currentcnt = 0
  soc = soc * 1000
  logfile = open('/media/75cc9171-4331-4f88-ac3f-0278d132fae9/test','w')
  sampletime = time.time()
  while True:
    try:
      for i in range(10):
        getraw()
        currentcnt = (currentcnt*9+rawcurrent)/10 # running av current in counts
#        print 'av current in counts', currentcnt
        current = currentcnt*256/50  # current in mv
#        print 'current in mv', current
        current = current*250/50 +000 # current in mamps
#        print 'current in amps', current
        voltages[0] = rawvolts[0]
#        printvoltage = str(round(rawvolts[0],3)).ljust(5,'0') + ' '
#        voltages[1] = rawvolts[1]*(2.49+33.2)/2.49 - voltages[0]
        for i in range(1,9):
          voltages[i] = (voltages[i]*9 + (rawvolts[i]-rawvolts[0])*(2.49+33.2)/2.49)/10
#          printvoltage = printvoltage + str(round(voltages[i],3)).ljust(5,'0') + ' '
#        print (printvoltage)
        time.sleep(0.1)
      vprint=''
      oldsampletime=sampletime
      sampletime = time.time()
      soc = soc + current*(sampletime-oldsampletime)/3600
      deltav[0]=voltages[0]
      deltav[1]=voltages[1] + calvolts[0]
      for i in range(8,1,-1):
        deltav[i]=round((voltages[i]-voltages[i-1]+calvolts[i-1]),3)
      for i in range(9):
        summary.data['hivolt'][i] = max(summary.data['hivolt'][i], deltav[i])
        summary.data['lowvolt'][i] = min(summary.data['lowvolt'][i],deltav[i])
        vprint=vprint + str(round(deltav[i],3)).ljust(5,'0') + ' '
      logdata = vprint + str(round(current/1000,1)) + ' ' + str(round(soc/1000,2)).ljust(5,'0') + '\n'  #  + '\033[1A'    
      sys.stdout.write(logdata)  #  + '\033[1A'    
      logfile.write(time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()+28800)) + logdata)
      summary.write()
    except KeyboardInterrupt:
      sys.stdout.write('\n')
      logfile.close()
      summary.close()
      break

if __name__ == "__main__":
  print (sys.argv)
  daemon(float(sys.argv[1]))
