"""Live ESP32 sensor serial -> aviation-style spoken observation -> DECtalk WAV.

Requires Windows, pyserial, and a separately obtained DECtalk runtime.
DECtalk files and credentials are deliberately not bundled in this repository.
"""
import ctypes
import os
import time
from datetime import datetime, timezone

import serial

from awos_weather import LINE_RE, build_awos_message, build_extended_awos_message

SERIAL_PORT = os.getenv("AWOS_SERIAL_PORT", "COM9")
BAUD = int(os.getenv("AWOS_BAUD", "115200"))
STATION_NAME = os.getenv("AWOS_STATION_NAME", "local")
STATION_ELEV_FT = float(os.getenv("AWOS_STATION_ELEV_FT", "36.0"))
AWOS_FORMAT = os.getenv("AWOS_FORMAT", "standard").lower()

ROOT = os.path.dirname(os.path.abspath(__file__))
DECTALK_DIR = os.path.abspath(os.getenv("AWOS_DECTALK_DIR", os.path.join(ROOT, "DECtalk_runtime")))
AWOS_WAV_FILE = os.path.abspath(os.getenv("AWOS_WAV_FILE", os.path.join(ROOT, "output", "latest_awos.wav")))

# DECTALK SETUP
# ============================================================

TTS_HANDLE = ctypes.c_void_p
WAVE_MAPPER = 0xFFFFFFFF
TTS_FORCE = 1
WAVE_FORMAT_1M16 = 0x00000004
DECTALK_SPEAKER = 2  # Harry voice
DECTALK_RATE = 165

_dll_search_handles = []


def load_dectalk():
    # Keep these handles alive for the whole program.
    _dll_search_handles.append(os.add_dll_directory(DECTALK_DIR))

    lib_dir = os.path.join(DECTALK_DIR, "lib")
    if os.path.isdir(lib_dir):
        _dll_search_handles.append(os.add_dll_directory(lib_dir))

    dll = ctypes.WinDLL(os.path.join(DECTALK_DIR, "DECtalk.dll"))

    dll.TextToSpeechStartup.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(TTS_HANDLE),
        ctypes.c_uint,
        ctypes.c_uint32,
    ]
    dll.TextToSpeechStartup.restype = ctypes.c_uint

    dll.TextToSpeechShutdown.argtypes = [TTS_HANDLE]
    dll.TextToSpeechShutdown.restype = ctypes.c_uint

    dll.TextToSpeechSetSpeaker.argtypes = [TTS_HANDLE, ctypes.c_uint32]
    dll.TextToSpeechSetSpeaker.restype = ctypes.c_uint

    dll.TextToSpeechSetRate.argtypes = [TTS_HANDLE, ctypes.c_uint32]
    dll.TextToSpeechSetRate.restype = ctypes.c_uint

    dll.TextToSpeechSpeak.argtypes = [
        TTS_HANDLE,
        ctypes.c_char_p,
        ctypes.c_uint32,
    ]
    dll.TextToSpeechSpeak.restype = ctypes.c_uint

    dll.TextToSpeechSync.argtypes = [TTS_HANDLE]
    dll.TextToSpeechSync.restype = ctypes.c_uint

    dll.TextToSpeechOpenWaveOutFile.argtypes = [
        TTS_HANDLE,
        ctypes.c_char_p,
        ctypes.c_uint32,
    ]
    dll.TextToSpeechOpenWaveOutFile.restype = ctypes.c_uint

    dll.TextToSpeechCloseWaveOutFile.argtypes = [TTS_HANDLE]
    dll.TextToSpeechCloseWaveOutFile.restype = ctypes.c_uint

    return dll


DECTALK = None  # Initialize the Windows DLL only when audio generation starts.


def write_awos_wav(text: str):
    global DECTALK
    if DECTALK is None:
        DECTALK = load_dectalk()

    os.makedirs(os.path.dirname(AWOS_WAV_FILE), exist_ok=True)
    temp_wav = os.path.join(os.path.dirname(AWOS_WAV_FILE), "latest_awos_temp.wav")

    if os.path.exists(temp_wav):
        try:
            os.remove(temp_wav)
        except OSError:
            pass

    old_directory = os.getcwd()
    handle = TTS_HANDLE()
    started = False
    wav_open = False

    try:
        os.chdir(DECTALK_DIR)

        result = DECTALK.TextToSpeechStartup(
            None,
            ctypes.byref(handle),
            WAVE_MAPPER,
            0,
        )
        if result != 0:
            raise RuntimeError(f"DECtalk startup failed: {result}")
        started = True

        result = DECTALK.TextToSpeechSetSpeaker(handle, DECTALK_SPEAKER)
        if result != 0:
            raise RuntimeError(f"DECtalk speaker failed: {result}")

        result = DECTALK.TextToSpeechSetRate(handle, DECTALK_RATE)
        if result != 0:
            raise RuntimeError(f"DECtalk rate failed: {result}")

        result = DECTALK.TextToSpeechOpenWaveOutFile(
            handle,
            temp_wav.encode("ascii"),
            WAVE_FORMAT_1M16,
        )
        if result != 0:
            raise RuntimeError(f"DECtalk WAV open failed: {result}")
        wav_open = True

        result = DECTALK.TextToSpeechSpeak(
            handle,
            text.encode("ascii", errors="replace"),
            TTS_FORCE,
        )
        if result != 0:
            raise RuntimeError(f"DECtalk speak failed: {result}")

        result = DECTALK.TextToSpeechSync(handle)
        if result != 0:
            raise RuntimeError(f"DECtalk sync failed: {result}")

        result = DECTALK.TextToSpeechCloseWaveOutFile(handle)
        wav_open = False
        if result != 0:
            raise RuntimeError(f"DECtalk WAV close failed: {result}")

        # Browser may briefly have the old WAV open on Windows.
        # Retry replacement for about two seconds before giving up.
        last_error = None
        for _ in range(20):
            try:
                os.replace(temp_wav, AWOS_WAV_FILE)
                last_error = None
                break
            except PermissionError as exc:
                last_error = exc
                time.sleep(0.1)

        if last_error is not None:
            raise last_error

    finally:
        if wav_open:
            try:
                DECTALK.TextToSpeechCloseWaveOutFile(handle)
            except Exception:
                pass

        if started:
            try:
                DECTALK.TextToSpeechShutdown(handle)
            except Exception:
                pass

        os.chdir(old_directory)


# ============================================================
# LIVE LOOP
# ============================================================

def main():
    print()
    print("========================================")
    print(" LOCAL AWOS - LIVE")
    print("========================================")
    print(f"Serial: {SERIAL_PORT} @ {BAUD}")
    print(f"WAV:    {AWOS_WAV_FILE}")
    print()
    print("Close Arduino Serial Monitor first.")
    print("Press CTRL+C to stop.")
    print()

    last_minute = None

    try:
        with serial.Serial(SERIAL_PORT, BAUD, timeout=2) as ser:
            time.sleep(1.5)
            print(f"[Serial] Listening on {SERIAL_PORT}...")

            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                match = LINE_RE.search(line)

                if not match:
                    print(f"[ESP32] {line}")
                    continue

                temp_c = float(match.group("temp_c"))
                rh = float(match.group("hum"))
                pres_hpa = float(match.group("pres"))

                now = datetime.now(timezone.utc)
                minute_id = now.strftime("%Y%m%d%H%M")

                # ESP32 sends sensor readings every second; generate one
                # new broadcast per UTC minute.
                if minute_id == last_minute:
                    continue

                last_minute = minute_id

                builder = build_extended_awos_message if AWOS_FORMAT == "extended" else build_awos_message
                message = builder(
                    temp_c, rh, pres_hpa,
                    station_name=STATION_NAME,
                    station_elev_ft=STATION_ELEV_FT,
                )

                print()
                print(f"[Snapshot {now.strftime('%H%MZ')}]")
                print(
                    f"Temp {temp_c:.2f} C | "
                    f"RH {rh:.1f}% | "
                    f"Pressure {pres_hpa:.1f} hPa"
                )
                print(message)

                write_awos_wav(message)
                print("[AWOS WAV] latest_awos.wav updated")

    except serial.SerialException as exc:
        print(f"\n[Serial error] {exc}")
        print(f"Check {SERIAL_PORT} and close Arduino Serial Monitor.")

    except KeyboardInterrupt:
        print("\nAWOS stopped.")


if __name__ == "__main__":
    main()
