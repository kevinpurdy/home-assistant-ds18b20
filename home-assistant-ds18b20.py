import paho.mqtt.client as mqtt 
import os
import socket
import json

import RPi.GPIO as GPIO

#  Set Pullup mode on GPIO14 first.
GPIO_PIN_NUMBER=14
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_NUMBER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

mqttBroker ="192.168.1.100" 
room = socket.gethostname()

client = mqtt.Client(f"{room} Room Temperature")
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
				temperatures.update({sensor:int(temperatureRaw)/1000})
				print(f"{sensor}: {int(temperatureRaw)/1000}")
			else:
				print("Sensor file doesn't have a valid temperature!")
	return temperatures

registerSensors()
loopCount = 0
while True:
	loopCount += 1
	if loopCount % 12 == 0:
		registerSensors()
	temperatures = readTemperature()
	for sensor in temperatures:
		client.publish(f"homeassistant/sensor/{room.lower()}/{sensor}/temperature", temperatures[sensor])
    
