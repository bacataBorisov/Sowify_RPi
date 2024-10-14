# Sowify - Serial Over Wi-Fy 

## Project description

This project aims to facilitate troubleshooting by eliminating the need for additional equipment and complex setups. It consists of two main components:

1. Raspberry Pi (RPi):

- Equipped with a MOXA uPort1150 for serial communication.
- Can use any RPi model having USB Type A (Model 3B+ used in this project).
- Battery-powered with serial signal conversion.

2. iOS Mobile App:

- Receives serial data sent by the RPi over Wi-Fi using an MQTT server.
- Devices must be on the same network (Wi-Fi or Ethernet).

### Features:

- Read/Write commands to/from equipment.
- Select preferred interface via Sowify app.
- Support for RS232/422/485 serial standards.
- MODBUS communication support (not yet implemented).

The following installation instructions apply to the setup of the RPi. More information about the mobile app an its usage can be found in a [separate section](https://github.com/bacataBorisov/Sowify_RPi/blob/master/README.md)

## Installation

The following installation instructions are valid for a fresh out of the box RPi. If you already have a device set-up and you are an advanced user you can ommit some of the steps.

1. Get a RPi and install Raspberry Pi OS - [How to install a Raspberry Pi OS?](https://www.raspberrypi.com/documentation/computers/getting-started.html#install-an-operating-system)
2. Install MOXA uPort 1150 Linux Drivers - the following kernels are supported by MOXA -> Kernel 6.x, 5.x, 4.x, 3.x, 2.6.x, and 2.4.x
  - [Download Drivers](https://cdn-cms.azureedge.net/getmedia/c7a1d4ee-ff6f-46fe-b707-e6e2c6fcc152/moxa-uport-1100-series-linux-kernel-6.x-driver-v6.0.tgz)
  - [Instructions for drivers installation](https://moxa.com/getmedia/a2924269-6076-4c8f-9c1e-7268e235dde1/moxa-uport-1100-series-manual-v9.0.pdf)
  - install **setserial** - `sudo apt-get install -y setserial`
  - install **pip3** - `sudo apt install python3-pip`
  - install **pyserial** - `sudo pip3 install pyserial`
3. Install and setup the Mosquitto MQTT Server on the RPi. There are different ways how to do that depending on your choice and the RPi operating system.
[I used this guide and I find it pretty well explained](https://forums.raspberrypi.com/viewtopic.php?t=196010)

## Usage

### **NB!** Check the configuration file of the MQTT server before starting it.

In order to make the server for public use you have to specify listener.
The following two lines of code need to be added to a custom configuration file: /etc/mosquitto/**filename**.conf, where
“filename” is the name of the file given by you:

```
#specify listener and port
listener 1883
#auth method
allow_anonymous true
```

If you want to set additional authentication method, you can check the documents here:
https://mosquitto.org/documentation/authentication-methods/

Start the server using the new configuration:
`sudo mosquito -v -c filename.conf`

- Download and save the mediator.py and sowify_client.py on the RPi (typically your home directory)
- make them executable `chmod +x sowify_client.py && chmod +x mediator.py`
- Start both scripts - `./sowify_client && ./mediator.py &`

With those steps completed you can now go to the [Sowify-iOS App Section](https://github.com/bacataBorisov/Sowify-iOS-App) and follow the instructions how to use the app and start seeing some serial data (make sure you have the uPort 1150 plugged in and a serial data source, otherwise you will get the relevant warning messages in the app)

### **TIP:** You can have your scripts running on start-up using some of the following methods [described in this link](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)

The "mediator.py" is solely responsible for rebooting and shutting down the RPi if anything goes wrong with the "sowify_client.py" or if you just want to reboot / power off your device remotely.

### **NOTE:** If you want to use the logging function, logs folder needs to be created individually by modifying the following line in the sowify_client.py
logging.basicConfig(filename=f"**your-log-dir-name-goes-here**/{log_timestamp}.log"

## **License**

Sowify is released under the MIT License. See the **[LICENSE](https://github.com/bacataBorisov/Sowify_RPi/blob/master/LICENSE.txt)** file for details.

## **Authors and Acknowledgment**

Sowify was created by **[Vasil Borisov](https://github.com/bacataBorisov)**.

Following resources have been used while developing project
- [PySerial](https://pypi.org/project/pyserial/)
- [MQTT](https://mqtt.org)
- [setserial](https://github.com/Distrotech/setserial)

## **Changelog**

- **0.1.0:** Initial release

## **Contact**

If you have any questions or comments about Sowify, please contact **[bacata.borisov](https://github.com/bacataBorisov)**.
