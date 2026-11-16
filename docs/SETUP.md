# Build and run

## Hardware

- An ESP32-based board connected by USB to a Windows PC.
- BME280 temperature, pressure and relative-humidity sensor (I²C address **0x77** in the firmware; change if your module is different).
- The Arduino **Adafruit BME280 Library** and **Adafruit Unified Sensor** dependencies.
- A local Windows installation of DECtalk with the needed DLLs and dictionaries, obtained and licensed separately.

The Arduino source calls `Wire.begin(SDA, SCL)`. Confirm the correct I²C pins and sensor power for your specific ESP32 board.

## 1. Upload sensor firmware

Open `firmware/awos/awos.ino` in Arduino IDE, install the Adafruit libraries, select the correct ESP32 board and USB port, and upload. The sensor must be found at `0x77` before output starts. Verify lines like:

```text
WX station ready.
Temp: 24.31 C  Hum: 63.4 %  Pres: 1012.8 hPa
```

Close Arduino Serial Monitor before starting Python so both processes do not compete for the same serial port.

## 2. Install Python requirements

From the project directory on Windows:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Configure local paths

Set the serial port, station details and a location for the locally installed DECtalk files. The scripts read standard environment variables, for example:

```powershell
$env:AWOS_SERIAL_PORT = "COM9"
$env:AWOS_STATION_NAME = "local"
$env:AWOS_STATION_ELEV_FT = "36"
$env:AWOS_DECTALK_DIR = "C:\Path\To\Your\DECtalk\AMD64"
```

The runtime directory should contain `DECtalk.dll` and its other required files in their expected relative locations. Keep license files and proprietary binaries outside version control. The selected voice is **Harry** and the configured rate is **165**.

By default the generated WAV is placed in `output/latest_awos.wav` in the project directory. If you override `AWOS_WAV_FILE`, set it consistently for both the generator and the server.

## 4. Start the generator

```powershell
python awos_live.py
```

The process reads the BME280 data over serial and creates a new spoken observation once each UTC minute. For the earlier long-form recording, set `$env:AWOS_FORMAT = "extended"` before launching.

## 5. Start the web server

In a separate terminal with the same environment:

```powershell
python awos_server.py
```

On the PC open **http://127.0.0.1:5000**. On a phone connected to the same local network, use **http://YOUR-PC-LAN-IP:5000**. The Flask app listens on the LAN by default; do not expose this development server directly to the Internet.

Click **LISTEN TO CURRENT AWOS** to load the latest WAV file. No audio is streamed over a VHF aviation radio frequency—the browser is the listening interface.

## Troubleshooting

- **`BME280 not found`**: Verify I²C address (`0x77`), power and SDA/SCL pins.
- **Serial port busy**: Close Arduino Serial Monitor, check the COM port, and reconnect.
- **No generated WAV**: Confirm Windows DECtalk runtime files, correct 64-bit DLL location and the directory in `AWOS_DECTALK_DIR`.
- **No WAV in the browser**: Check that the generator has run and the server uses the same `AWOS_WAV_FILE` path.
- **No access from phone**: Confirm same LAN, correct IP, and Windows Firewall settings for port 5000.
