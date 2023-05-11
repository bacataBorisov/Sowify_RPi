#!/usr/bin/env python3
import subprocess
import os
import re
import time
from datetime import date, datetime
import logging
import serial
import paho.mqtt.client as mqtt

#set logging settings
log_timestamp = datetime.today().isoformat()
#comment this section and all the rest containing "loging. " 
#if you don't want to use logging feature. However if you want to use them,
#create the appropriate folders in your project

logging.basicConfig(filename=f"/home/pi/sowify/logs/operator/{log_timestamp}.log",
encoding='utf-8',
format='%(asctime)s %(message)s', 
datefmt='%d/%m/%Y %I:%M:%S %p', 
level=logging.DEBUG)

# create an instance of the serial port that we will open later
ser = serial.Serial()

# set connecting client ID
broker_adress = "localhost"
topic_ios = "getData"
topis_ios_feedback = "feedback"
topic_warning = "warning"
topic_cmd = "command"
ser_conf_topic = "configuration"
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
client = mqtt.Client(f"RPi OPERATOR with id: [{getserialID()}]")

# connect to the broker & subscribe to topics
client.connect("localhost", 1883, 60)
client.subscribe(ser_conf_topic)
client.subscribe(topic_cmd)
client.subscribe(topic_mediator)
client.loop_start()

#define on_connect callback 
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag = True #set flag
        print("connected OK Returned code=",rc)
        logging.warning("Connected!")
    else:
        print("Bad connection Returned code= ",rc)
        logging.warning(f"Bad connection with rc = : ", rc)

#define the on_disconnect callback - this has to be logged with timestamp - heck how??
def on_disconnect(client, userdata, rc):

    print("disconnecting reason  "  +str(rc))
    logging.warning(f"Reason for disconnection: ", str(rc))
    client.connected_flag=False
    client.disconnect_flag=True

# callback function when msg is received
def on_message(client, userdata, msg):

    msg_decoded = msg.payload.decode()

    #decode the command and send the configuration vie shell

    if msg.topic == ser_conf_topic:

        print(msg_decoded)
        x = msg_decoded.split(",", 5)

        interface = x[0]
        baudrate = x[1]
        parity = x[2]

        #this is a little bit over-engineered but I just wanted to make sure that I pass the proper stopbit constant
        if x[3] == '1':
            stopbits = serial.STOPBITS_ONE
            stopbits_number = 1
        elif x[3] == '1.5':
            stopbits = serial.STOPBITS_ONE_POINT_FIVE
            stopbits_number = 1.5
        else:
            stopbits = serial.STOPBITS_TWO
            stopbits_number = 2

        bytesize = int(x[4])

        port_settings = {'baudrate': baudrate, 'bytesize': bytesize, 'parity': parity, 'stopbits': stopbits_number}
        ser.stopbits = stopbits
        
        #close port before applying settings
        ser.close()
        #this is just an extra check, I don't know if I am going to need it
        if ser.is_open == False:

            #setting uPort 1150 settings
            cmd = 'setserial /dev/ttyUSB0 port '+interface
            y = subprocess.run(cmd, shell = True)
            #configure and open the serial port
            ser.port = '/dev/ttyUSB0'
            #ser.apply_settings(settings) - this is still possible to be done in later stage
            ser.apply_settings(port_settings)

            # define dictionary for the RS types
            # uPort 1150 configuration - from their readme.txt file on the RPi
            # parameter   value   interface
            # 
            # port        0       RS-232
            #             1       RS-485 2W
            #             2       RS-422
            #             3       RS-485 4W
            #return feedback to the ios app

            if interface == '1':
                interface_dcd = 'RS-485 2W'
            elif interface == '2':
                interface_dcd = 'RS-422'
            elif interface == '3':
                interface_dcd = 'RS-485 4W'
            else:
                interface_dcd = 'RS-232'
            client.publish(topis_ios_feedback, f"{interface_dcd}, {baudrate} bits/s, {parity}, {bytesize}, {stopbits_number}", qos=2)
            #port timeout
            ser.timeout = 1
            #last check of the settings
            logging.info(f"last settings check before opening {ser.get_settings()}")
            print(f"last settings check before opening {ser.get_settings()}")
            #open port
            try:
                ser.open()
            except serial.SerialException as sererr:
                #return error code and show in the status bar together with play button disabled - HERE!!!
                logging.warning(f"SerialException from on_message(): {sererr}")
                print(f"SerialException from on_message(): {sererr}")
                client.publish(topic_warning, "Serial Converter Unplugged")
                time.sleep(1)
            
            read_serial()

    elif msg.topic == topic_cmd:
        write_serial(msg_decoded)
    elif msg.topic == topic_mediator:
        if msg_decoded == "reboot":
            client.loop_stop()
            client.disconnect()
        else: 
            client.loop_stop()
            client.disconnect()
    else:
        # to be done in better way
        print("Unknown message!")

def read_serial():

    #listen for new changes on_message
    client.loop_start()

    try:
        while ser.in_waiting > 0:
            #print(ser.in_waiting)
            data = ser.readline().decode('utf-8')    
            client.publish(topic_ios, data)

    #adding 1 second in the exception so it doesn't go to infite cycle - explain it better
    #catching different exceptions that occured during tests
    except TypeError as typerr:
        logging.warning(f"TypeError from read_serial: {typerr}")
        print(f"TypeError from read_serial: {typerr}")
        client.publish(topic_warning, "Serial Converter Unplugged")
        time.sleep(1)
    except OSError as oserr:
        logging.warning(f"OSError from read_serial: {oserr}")
        print(f"OSError from read_serial: {oserr}")
        #close the port so /dev/ttyUSB0 is not changed
        if ser.is_open == True:
            ser.close()
        #client.publish(topic_warning, "Serial Converter Unplugged")
        time.sleep(1)
    except UnicodeDecodeError as unierr:
        logging.info(f"UnicodeDecodeError from read_serial: {unierr}")
        print(f"UnicodeDecodeError from read_serial: {unierr}")  
        #client.publish(topic_warning, "Check polarity & IOIOI Settings")
    except AttributeError as atterr:
        logging.info(f"AttributeError from read_serial: {atterr}")
        print(f"AttributeError from read_serial: {atterr}")
        #client.publish(topic_warning, "Serial Port Not Configured Yet")
        time.sleep(1)


#functions to send commands to the device
def write_serial(message):
    if ser.is_open == True:
        ser.write(message.encode('utf-8'))
    else: 
        print("From write_serial(): Port is not opened!")
        client.publish(topic_warning, "Port is not opened")
#mqtt callback functions go here
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# #open port - hold it for now, I am not sure if I am going to need it
# try:
#     #initial port settings
#     ser.port = '/dev/ttyUSB0'
#     initial_port_settings = {'baudrate': 9600, 'bytesize': 8, 'parity': 'N', 'stopbits': 1}
#     ser.apply_settings(initial_port_settings)
#     ser.open()
#     print(f"initial settings {ser.get_settings()}")
# except serial.SerialException as sererr:
#     #return error code and show in the status bar together with play button disabled - HERE!!!
#     logging.warning(f"SerialException from on_message(): {sererr}")
#     print(f"SerialException from on_message(): {sererr}")
#     client.publish(topic_warning, "Serial Converter Unplugged")
#     time.sleep(1)



#infinte loop
while True:
    client.loop_stop()
    read_serial()
