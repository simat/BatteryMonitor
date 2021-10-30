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

broker = '192.168.2.123'
port = 1883
topic = "power"
# username = 'emqx'
# password = 'public'

def connect_mqtt():
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

  client = mqtt_client.Client('karrak_power_supply')
#    client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

client=connect_mqtt()
client.loop_start()

def publish(topic,data):
  result = client.publish(topic, data)
  # result: [0, 1]
  status = result[0]
  if status == 0:
      print(f"Send `{data}` to topic `{topic}`")
  else:
      print(f"Failed to send message to topic {topic}")

def test():
  client.loop_start()
  count =0
  while True:
    count+=1
    publish(client,'batpwr',data=f"SOC:{count},powerin:{count}")
    publish(client,'solarpwr',data=f"SOC:{count},powerin:{count}")
    publish(client,'loadpwr',data=f"SOC:{count},powerin:{count}")

    sleep(2)
