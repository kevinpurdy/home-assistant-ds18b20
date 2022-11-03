# home-assistant-ds18b20

A simple Python app that reads temperature values from DS18B20 1-Wire sensors and reports to an MQTT broker in a format compatible with Home Assistant.

On initialisation (and periodically) a message is published to the HA config MQTT topic to add the temperature sensors to Home Assistant using the MQTT Discovery service.

## Hardware Setup

This is expected to run on a Raspberry Pi - tested on both the Pi4 and Pi2.

Connect DS18b20 1-Wire sensor(s) to the Raspberry Pi and enable 1-wire using the Raspberry Pi configuration tool.

If you are using a non-standard GPIO pin for 1-wire, don't forget to specify the GPIO pin in `config.txt`, e.g: `dtoverlay=w1-gpio,gpiopin=14`

## Installation

You'll need an MQTT broker, the code assumes you are using the Home Assistant Mosquitto MQTT brtoker add-on.

### Download and Install Dependencies

Clone this repo:

```bash
git clone https://github.com/philprobinson84/home-assistant-ds18b20.git
cd home-assistant-ds18b20
```

Install dependencies:

```bash
pip3 install -r requirements.txt
```

### Configuration

All parameters are defined in the YAML file, with comments indicating the function of each configuration option:

```yaml
####################################################################
# 1-Wire configuration
1-wire:
  # GPIO pin used for 1-wire bus, using GPIO/BCM naming convention
  # See pinout.xyz for pin numbering info
  gpio: 4
  # Define whether an external 4.7k pull-up resistor is fitted
  # Set to true if using an external 4.7k pull-up resistor
  # If set to false, the script will enable the internal pull-up
  external-pullup: false
####################################################################
# MQTT configuration
mqtt:
  # IP address of the MQTT broker
  ip: localhost
  # Username to be used with the MQTT broker
  username: homeassistant
  # Password to be used with the MQTT broker
  password: mqttpass
####################################################################
# Sensor configuration
sensor:
  # Room name, sensor will be named: {room} temperature {count}
  # If below line is left commented, hostname will be used
  # room: office
  # Registration frequency, sensors will be registered every nth sensor reading
  registration-frequency: 10
  # Reporting frequency in seconds
  frequency: 30
####################################################################
```

As a minimum, you will need to set the password for the MQTT broker.

### Install as a Service

Copy script and config to expected location:

```bash
cp ./home-assistant-ds18b20.py /usr/bin/
cp ./home-assistant-ds18b20.yaml /usr/bin/
```

Copy service file:

```bash
sudo cp ./home-assistant-ds18b20.service /lib/systemd/system/
```

Reload the system manager:
```bash
sudo systemctl daemon-reload
```

Enable the service:
```bash
sudo systemctl enable home-assistant-ds18b20.service
```

Start the service
```bash
sudo systemctl start home-assistant-ds18b20.service
```

Check status:
```bash
sudo systemctl status home-assistant-ds18b20.service
```

As long as Home Assistant is already integrated wih your MQTT broker, a new temperature sensor will be registered with Home Assistant.
