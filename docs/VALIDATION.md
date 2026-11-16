# Validation and next experiments

## Source-level checks

- Python unit tests exercise BME280 serial-line parsing, dewpoint/pressure calculations, and aviation phrase formatting.
- Python scripts are syntax-checked without loading proprietary DECtalk binaries.
- The ESP32 firmware's serial layout matches the Python regex.

## On-device experiments

- Confirm stable 1 Hz BME280 telemetry over USB and logging of dropped/invalid lines.
- Compare BME280 temperature, humidity and pressure with a local reference instrument.
- Verify generated WAV playback in the local web page across consecutive UTC-minute updates.
- Record timestamping and time-zone behavior on a Windows host.
- Measure audio update latency and server response times.
- Add an anemometer/wind-direction sensor and a dedicated visibility measurement method if expanding the hardware.

## Engineering distinctions

The unit has sensors for **temperature, relative humidity and pressure**. Dewpoint, pressure/density altitude and altimeter setting are calculated quantities. The visibility phrase in the code is a moisture-based **estimate**, not a sensor measurement. Wind and ceiling are not measured. This makes the station suitable for embedded weather-data and speech-interface experimentation, not operational aviation weather observations.
