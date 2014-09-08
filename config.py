from ast import literal_eval
from ConfigParser import SafeConfigParser

class Config:
  def __init__(self):
    configfile = SafeConfigParser()
    configfile.read('battery.cfg')
    self.config = {}
    for section in configfile.sections():
      self.config[section] = {}
      for key, val in configfile.items(section):
        self.config[section][key] = literal_eval(val)


config = Config()
config = config.config

