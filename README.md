# ESP32 Automated Aviation Weather Station (AWOS-Inspired)

**ESP32 + BME280 environmental sensing · Python weather calculations · DECtalk voice synthesis · Flask web interface**

I built a miniature aviation weather-observation system to explore how environmental sensor readings can be turned into the spoken weather reports pilots are accustomed to hearing. An **ESP32** reads temperature, relative humidity and barometric pressure from a **BME280**. A Python application processes the measurements, computes additional weather values, and generates an aviation-style voice bulletin using **DECtalk**. I can then open a local webpage on a computer or phone and listen to the latest observation.

The interesting part for me was connecting the entire chain—from an I²C sensor and USB serial data stream to atmospheric calculations, speech synthesis and a web-accessible audio interface.

## What I built

- **Embedded sensor acquisition:** ESP32 polls the BME280 at **1 Hz** over I²C and sends labeled readings over USB serial at **115200 baud**.
- **Python processing:** parses the live serial measurements and calculates dew point (Magnus approximation), altimeter setting, pressure altitude and density altitude.
- **Aviation-style message generation:** builds a UTC/Zulu-timestamped observation with digit-by-digit number pronunciation and a configurable station name/elevation.
- **DECtalk voice output:** uses the Windows DECtalk API through Python `ctypes` to generate a spoken WAV recording, updated **once per UTC minute**.
- **Local listening page:** Flask serves the current WAV recording through a simple responsive page that I can open from a phone on the same network.
- **Configurable setup:** COM port, station settings, audio paths and server address can be set through environment variables without modifying the source.

## System overview

```mermaid
flowchart LR
    S[BME280] -->|I²C| E[ESP32]
    E -->|USB serial| P[Python weather processor]
    P --> M[AWOS-style message]
    M --> D[DECtalk synthesis]
    D --> W[Updated WAV file]
    W --> F[Flask web page]
    F --> U[Listen on computer / phone]
```

## How the observation works

For each reading, the ESP32 transmits a line such as:

```text
Temp: 24.31 C  Hum: 63.4 %  Pres: 1012.8 hPa
```

The Python processor extracts the measurements, calculates derived weather values and creates an observation like:

> Local automated weather observation. Time one eight four five zulu. Wind not available. Estimated visibility greater than ten statute miles. Sky conditions not available. Temperature two four celsius. Dew point one seven celsius. Altimeter two niner niner two. Remarks. Density altitude ... feet.

*Illustrative format, not a captured recording.* The voice uses the DECtalk **Harry** speaker at a configured speech rate of 165. The "+1 minute" update timing is keyed to UTC, with the most recent WAV file replaced after synthesis.

**Sensor coverage:** Temperature, humidity and pressure are measured; dew point and altitudes are calculated. The current visibility phrase is a humidity/dewpoint-spread heuristic rather than a direct visibility measurement. Wind and ceiling sensors are potential hardware expansions.

## Software and hardware

| Component | Function |
| --- | --- |
| ESP32 development board | I²C acquisition and USB serial link |
| BME280 | Temperature, humidity and pressure sensor |
| Python + pyserial | Reads and parses the measurements |
| Python math layer | Dewpoint, altimeter and density-altitude calculations |
| DECtalk on Windows | Generates spoken aviation-style weather observations |
| Flask | Serves the updated WAV with a browser audio player |

## Project structure

```text
firmware/awos/awos.ino     ESP32/BME280 Arduino sketch
awos_weather.py           Serial parser, calculations and speech formatting
awos_live.py              Serial acquisition and DECtalk WAV generation
awos_server.py            Flask page and audio endpoint
docs/                     Architecture, setup and development notes
tests/                    Weather calculation and message-format tests
.github/workflows/        Python syntax and unit-test CI
```

## Getting started

1. Upload [the ESP32 Arduino firmware](firmware/awos/awos.ino) using the Adafruit BME280 library. The default sensor I²C address is `0x77`.
2. On a Windows PC, install Python dependencies: `pip install -r requirements.txt`.
3. Configure your local serial port and DECtalk installation with `AWOS_SERIAL_PORT` and `AWOS_DECTALK_DIR`. **DECtalk is an external runtime**, not distributed in this repository.
4. Start the live observation generator with `python awos_live.py`.
5. Start the listening page in a second terminal with `python awos_server.py`; visit **http://127.0.0.1:5000** or your PC's LAN IP from a phone.

Complete instructions and configuration examples are in [docs/SETUP.md](docs/SETUP.md).

## Tests and next steps

Run offline checks for the serial parser, atmospheric calculations, and message formatting:

```bash
python -m unittest discover -s tests -v
```

I'm planning to add an anemometer for wind speed/direction, a dedicated visibility sensor, hardware calibration against reference readings, and a short recording/video demonstrating the complete sensor-to-web workflow.

## Dependencies and credits

This project uses the Adafruit BME280 sensor library, pyserial, Flask, and a separately installed Windows DECtalk speech runtime. The DECtalk binaries, dictionaries, licensing configuration, and generated audio files are not part of this source repository. See [third-party dependencies](docs/THIRD_PARTY.md).

**Project scope:** A personal embedded-systems and aviation-software prototype. The audio bulletin is not an official airport weather broadcast or a substitute for certified observations.
