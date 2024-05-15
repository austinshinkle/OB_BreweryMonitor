# :beer: Ostentatious Brewing Brewery Monitor
## About
This repository contains python scripts for Raspberry Pi (target HW is Pi Zero 2 W), which supports my homebrewing setup. The overall setup consists of two fermentation chambers based on chest freezers with temperature controllers and a kegerator that supports two corny kegs built from a minifridge.

## Components

### Fermentation Chambers
Each fermentation chamber supports a 40L Spiedel Fermenter and has a temperature controller connected to the freezer power (cold side) and a reptile heater (warm side). Additionally, each chamber has a chamber temperature sensor and Tilt Hydrometer (under development) connected to the RPI Zero 2 W to monitor fermentation.

### Kegerator
The kegerator fits two corny kegs with picnic taps. The kegerator has an interior temperature sensor and a load cell under each keg connected to the RPI Zero 2 W to measure the amount of beer remaining in each keg.

### Monitoring System
The monitor is implemented in a Raspberry Pi Zero 2 W and hosts a socket that collects the data and serializes it into a stream which provides the sensor data. The visualization must be completed separately by connecting to the socket provided by the monitor.

## Schematic
![Schematic](BreweryMonitor.drawio.svg)

![OB](/media/OstentatiousBrewingRobot.jpeg)
