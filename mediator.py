#!/usr/bin/env python3

import subprocess
import os
import re
import time
import paho.mqtt.client as mqtt

topic_mediator = "mediator"

#get RPi ID unique number
def getserialID():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial

# create instance of the client and set client namee
client = mqtt.Client(f"RPi MEDIATOR with id: [{getserialID()}]")

# connect to the broker & subscribe to topics
client.connect("localhost", 1883, 60)
client.subscribe(topic_mediator, qos=2)

def on_message(client, userdata, msg):
  
    msg_decoded = msg.payload.decode()
    print(msg_decoded)
    if msg_decoded == "reboot":
        time.sleep(2)
        #setting uPort 1150 settings
        cmd = 'sudo reboot now'
        y = subprocess.run(cmd, shell = True)
    elif msg_decoded == "shutdown":
        time.sleep(2)
        cmd = 'sudo shutdown now'
        y = subprocess.run(cmd, shell = True)

#mqtt callback functions go here
client.on_message = on_message

while True:

    client.loop_forever()
