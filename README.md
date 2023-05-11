##Sowify - Serial Over Wi-Fy

*Project description*

This project is intended to be used for reading a serial signal by means of MOXA uPort1150 serial-to-USB adapter and
send it over the wi-fi local network. The main controller is a Raspberry Pi which handles the reading and sending the data
to an iOS app that will be displayed it on the user's iPhone or iPad. The implemented communication is two-way - reading and 
writing to the serial port. MODBUS is not supported yet

For successfully using this project you will need following elements (they can all be found in the git dir)
1. Raspberry Pi controller (I am using 3B+ at that time)
2. MOXA uPort 1150 - USB-to-serial adapter (I am using 1-port version)
3. iOS application "Sowify" installed.
4. all must be connected to the same network (wi-fi or adhoc)

If devices are to be different code must be altered accordingly.

The read data is being sent over the network via MQTT websocket communication. RPi acts simultaneously as a server and a client.
Mosquitto server runs with a custom configuration file located in : **/etc/mosquitto/conf.d/sowify.conf**

There is a separate script called "mediator.py" which is solely responsible for rebooting and shutting down the raspberry pi,
if anything goes wrong with the "sowify_client" or you just want to power your device remotely.

**If you want to use the logging function, logs folder needs to be created individually and you pick the best location that is suitable for you** 
