"""Serial weather parsing, BME280-derived calculations and spoken observation formatting.

Adapted from the original awos_live_exact_format.py and awos_live.py scripts.
The two spoken formats reproduce the project's original calculation/phrasing logic.
"""

import math
import re
from datetime import datetime, timezone

# ESP32 SERIAL FORMAT
# ============================================================

# Expected line:
# Temp: 25.14 C  Hum: 51.8 %  Pres: 1012.7 hPa
LINE_RE = re.compile(
    r"Temp:\s*(?P<temp_c>-?\d+(?:\.\d+)?)\s*C.*?"
    r"Hum:\s*(?P<hum>-?\d+(?:\.\d+)?)\s*%.*?"
    r"Pres:\s*(?P<pres>-?\d+(?:\.\d+)?)\s*hPa",
    re.IGNORECASE,
)


# ============================================================
# WEATHER CALCULATIONS
# ============================================================

def dewpoint_c_magnus(temp_c: float, rh_percent: float) -> float:
    rh = max(0.1, min(100.0, rh_percent))
    b = 17.625
    c = 243.04
    gamma = math.log(rh / 100.0) + (b * temp_c) / (c + temp_c)
    return (c * gamma) / (b - gamma)


def pressure_altitude_ft_from_station_mb(p_mb: float) -> float:
    return 145366.45 * (1.0 - (p_mb / 1013.25) ** 0.190284)


def altimeter_setting_mb_from_station_mb(p_mb: float, elev_ft: float) -> float:
    elev_m = elev_ft * 0.3048
    base = 1.0 - (0.0065 * elev_m) / 288.15
    return p_mb / (base ** 5.255877)


def mb_to_inhg(p_mb: float) -> float:
    return p_mb / 33.8638866667


def density_altitude_ft(pressure_alt_ft: float, oat_c: float) -> float:
    isa_temp_c = 15.0 - 1.98 * (pressure_alt_ft / 1000.0)
    return pressure_alt_ft + 120.0 * (oat_c - isa_temp_c)


def estimate_visibility(temp_c: float, dew_c: float, rh: float) -> str:
    # Experimental moisture/fog-based estimate only.
    spread = temp_c - dew_c

    if rh >= 99 or spread <= 0.2:
        return "less than one statute mile"
    elif rh >= 97 or spread <= 0.5:
        return "one to three statute miles"
    elif rh >= 94 or spread <= 1.0:
        return "three to five statute miles"
    elif rh >= 90 or spread <= 2.0:
        return "five to seven statute miles"
    elif rh >= 85 or spread <= 3.0:
        return "seven to ten statute miles"
    else:
        return "greater than ten statute miles"


# ============================================================
# AWOS PHRASEOLOGY
# ============================================================

DIGIT_WORDS = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "niner",
}


def speak_digits(value) -> str:
    return " ".join(DIGIT_WORDS[d] for d in str(value) if d in DIGIT_WORDS)


def signed_number_phrase(value: float) -> str:
    number = int(round(value))
    if number < 0:
        return "minus " + speak_digits(abs(number))
    return speak_digits(number)


def altimeter_phrase(inhg: float) -> str:
    return speak_digits(f"{inhg:.2f}".replace(".", ""))


def build_awos_message(temp_c: float, rh: float, pres_hpa: float, station_name: str = "local", station_elev_ft: float = 36.0, when: datetime | None = None) -> str:
    dew_c = dewpoint_c_magnus(temp_c, rh)
    pressure_alt_ft = pressure_altitude_ft_from_station_mb(pres_hpa)

    altimeter_mb = altimeter_setting_mb_from_station_mb(
        pres_hpa,
        station_elev_ft,
    )
    altimeter_inhg = mb_to_inhg(altimeter_mb)

    density_alt_ft = density_altitude_ft(
        pressure_alt_ft,
        temp_c,
    )

    visibility = estimate_visibility(temp_c, dew_c, rh)
    zulu = (when or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%H%M")

    # Exact broadcast order:
    # local automated weather observation
    # time
    # wind N/A
    # estimated visibility
    # sky conditions N/A
    # temperature
    # dew point
    # altimeter
    # remarks
    # density altitude
    return (
        f"{station_name} automated weather observation. "
        f"Time {speak_digits(zulu)} zulu. "
        f"Wind not available. "
        f"Estimated visibility {visibility}. "
        f"Sky conditions not available. "
        f"Temperature {signed_number_phrase(temp_c)} celsius. "
        f"Dew point {signed_number_phrase(dew_c)} celsius. "
        f"Altimeter {altimeter_phrase(altimeter_inhg)}. "
        f"Remarks. "
        f"Density altitude {signed_number_phrase(density_alt_ft)} feet."
    )


# ============================================================


def build_extended_awos_message(temp_c: float, rh: float, pres_hpa: float, station_name: str = "local", station_elev_ft: float = 36.0, when: datetime | None = None) -> str:
    dew_c = dewpoint_c_magnus(temp_c, rh)
    pressure_alt_ft = pressure_altitude_ft_from_station_mb(pres_hpa)

    altimeter_mb = altimeter_setting_mb_from_station_mb(
        pres_hpa,
        station_elev_ft,
    )
    altimeter_inhg = mb_to_inhg(altimeter_mb)

    density_alt_ft = density_altitude_ft(
        pressure_alt_ft,
        temp_c,
    )

    visibility = estimate_visibility(temp_c, dew_c, rh)
    zulu = (when or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%H%M")

    return (
        f"{station_name} automated weather observation. "
        f"Time {speak_digits(zulu)} zulu. "
        f"Estimated visibility {visibility}. "
        f"Temperature {signed_number_phrase(temp_c)} celsius. "
        f"Dew point {signed_number_phrase(dew_c)} celsius. "
        f"Altimeter {altimeter_phrase(altimeter_inhg)}. "
        f"Remarks. Experimental station. "
        f"Visibility is an experimental humidity based estimate. "
        f"Pressure altitude {signed_number_phrase(pressure_alt_ft)} feet. "
        f"Density altitude {signed_number_phrase(density_alt_ft)} feet. "
        f"Cloud information not available. "
        f"Wind information not available."
    )
