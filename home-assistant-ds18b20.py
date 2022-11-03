import paho.mqtt.client as mqtt 
import os
import socket
import json
import yaml
import sys
from time import sleep
import RPi.GPIO as GPIO

# Get config
try:
    config = yaml.safe_load(open("home-assistant-ds18b20.yaml"))
except:
    sys.exit("Problem loading config.yaml!")

# Configure GPIO
try:
    GPIO_PIN_NUMBER = config['1-wire']['gpio']
except:
    sys.exit("No 1-wire GPIO specified in config.yaml!")
GPIO.setmode(GPIO.BCM)

try:
	GPIO_EXTERNAL_PU = config['1-wire']['external-pullup']
except:
	sys.exit("No GPIO pull-up specified in config.yaml!")

if GPIO_EXTERNAL_PU:
	GPIO.setup(GPIO_PIN_NUMBER, GPIO.IN)
else:
	GPIO.setup(GPIO_PIN_NUMBER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Get MQTT broker info from config.yaml
try:
	mqttBroker = config['mqtt']['ip']
except:
	sys.exit("No MQTT Broker IP address specified in config.yaml!")

try:
	mqttUser = config['mqtt']['username']
	mqttPass = config['mqtt']['password']
except:
	sys.exit("No MQTT Broker Username/Password specified in config.yaml!")

# Get room name, fallback to hostname if not specified
try:
	room = config['sensor']['room']
except:
	print("No sensor name specified in config.yaml, using hostname.")
	room = socket.gethostname()

# Get reporting frequency
try:
	frequency = config['sensor']['frequency']
except:
	print("No sensor reporting frequency specified in config.yaml, using 30s.")
	frequency = 30

# Get registration frequency
try:
	registration = config['sensor']['registration-frequency']
except:
	print("No sensor registration frequency specified in config.yaml, using 10.")
	registration = 10

# Connect to MQTT Broker
client = mqtt.Client(f"{room} Room Temperature")
client.username_pw_set(mqttUser, mqttPass)
client.connect(mqttBroker)
client.loop_start()

path1 = "/sys/bus/w1/devices/"
path2 = "/w1_slave"
	
def registerSensors():
	sensors = os.listdir( path1 )
	count = 0
	for sensor in sensors:
		if sensor.startswith("28"):
			count += 1
			config = {"name": f"{room} temperature {count}", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": f"homeassistant/sensor/{room.lower()}/{sensor}/temperature"}
			print(f"Registering sensor: {config}")
			client.publish(f"homeassistant/sensor/{room.lower()}/{sensor}/config", json.dumps(config))

def readTemperature():	
	sensors = os.listdir( path1 )
	temperatures = {}
	for sensor in sensors:
		if sensor.startswith("28"):
			sensorFile = open(f"{path1}{sensor}{path2}","r")
			line = sensorFile.readline()
			if line.find("YES") != -1:
				line = sensorFile.readline()
				temperatureRaw = line.split('=')[1]
				temperatureRaw = temperatureRaw[:-1] # remove the line ending...
				temperatures.update({sensor:round(int(temperatureRaw)/1000,1)})
				print(f"{sensor}: {round(int(temperatureRaw)/1000,1)}")
			else:
				print("Sensor file doesn't have a valid temperature!")
	return temperatures

registerSensors()
loopCount = 0
while True:
	loopCount += 1
	if loopCount % registration == 0:
		registerSensors()
	temperatures = readTemperature()
	for sensor in temperatures:
		client.publish(f"homeassistant/sensor/{room.lower()}/{sensor}/temperature", temperatures[sensor])
	sleep(frequency)
