#!/usr/bin/python
# *****BatteryMonitor MQTT client*****
# Copyright (C) 2021 Simon Richard Matthews
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

from paho.mqtt import client as mqtt_client
from time import sleep
from config import editbatconfig
import logger
log = logger.logging.getLogger(__name__)
log.setLevel(logger.logging.DEBUG)
log.addHandler(logger.errfile)

broker = '192.168.1.94'
port = 1883
topic = "power"
username = 'karrak'
password = 'simat6811'

def on_message(client,userata,message):
  """Executed when any subscribed MQTT message arives
  At present assumes payload is item to change in battery.config
  makes change and rewrites config file"""

  payload=eval(str(message.payload.decode("utf-8")))
  print (payload)
  for section in payload:
    for item in payload[section]:
#      print (section,item,payload[section][item])
      editbatconfig(section,item,payload[section][item])

def on_disconnect(client, userdata, rc):
  if rc:
    log.error('MQTT server disconnect, Restart MQTT')

def connect_mqtt():
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to MQTT Broker!")
    else:
      fail=f"Failed to connect, return code {rc}"
      print(fail)
      log.error(fail)

  client = mqtt_client.Client('karrak_power_supply',clean_session=False)
  client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

client=connect_mqtt()
client.on_message=on_message
client.on_disconnect=on_disconnect
client.subscribe("karrak/energy/settings",qos=1)
client.loop_start()

def publish(topic,data):
  result = client.publish(topic, data)
  # result: [0, 1]
  status = result[0]
  if status == 0:
    print(f"Send `{data}` to topic `{topic}`")
  else:
    fail=f"MQQT Failed to send message to topic {topic}"
    print(fail)
    log.error(fail)


def test():
  client.loop_start()
  count =0
  while True:
    count+=1
    publish(client,'batpwr',data=f"SOC:{count},powerin:{count}")
    publish(client,'solarpwr',data=f"SOC:{count},powerin:{count}")
    publish(client,'loadpwr',data=f"SOC:{count},powerin:{count}")

    sleep(2)
