# home-assistant-ds18b20

A simple Python app that reads temperature values from DS18B20 1-Wire sensors and reports to an MQTT broker in a format compatible with Home Assistant.

On initialisation a message is published to the config MQTT topic to add the temperature sensors to Home Assistant using the MQTT Discovery service.

The sensor name added to Home Assistant is the Host Name of the sensor, typically a Raspberry Pi.

## Hardware Setup

This is expected to run on a Raspberry Pi - tested on both the Pi4 and Pi2.

Connect a single DS18b20 1-Wire sensor to the Pi's 3V3, GPIO4 (pin 7) and GND pins, with a 4.7K resistor between 3V3 and GPIO4.

## Installation

You'll need an MQTT broker, the code assumes it's on the same machine. In the code, change `localhost` to match the IP of the MQTT broker if this is not the case.

Clone this repo.

The only dependency is `paho-mqtt`:

```bash
pip3 install paho-mqtt
```

## Usage
Run:

```bash
python3 home-assistant-ds18b20.py
```

As long as Home Assistant is already integrated wih your MQTT broker, a new temperature sensor will be registered with the name: ` `
