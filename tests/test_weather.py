"""Offline unit tests for the Python weather and observation-format layer."""
import datetime
import math
import unittest

from awos_weather import (
    LINE_RE, altimeter_phrase, build_awos_message, build_extended_awos_message,
    density_altitude_ft, dewpoint_c_magnus, estimate_visibility,
    mb_to_inhg, pressure_altitude_ft_from_station_mb, signed_number_phrase,
    speak_digits,
)


class WeatherTests(unittest.TestCase):
    def test_serial_message(self):
        m = LINE_RE.search("Temp: 24.31 C  Hum: 63.4 %  Pres: 1012.8 hPa")
        self.assertIsNotNone(m)
        self.assertAlmostEqual(float(m.group("temp_c")), 24.31)
        self.assertAlmostEqual(float(m.group("hum")), 63.4)
        self.assertAlmostEqual(float(m.group("pres")), 1012.8)

    def test_serial_negative_temperature(self):
        m = LINE_RE.search("Temp: -5.50 C Hum: 90.0 % Pres: 990.1 hPa")
        self.assertEqual(m.group("temp_c"), "-5.50")

    def test_dewpoint(self):
        self.assertAlmostEqual(dewpoint_c_magnus(20, 50), 9.25, delta=0.1)

    def test_sea_level_pressure_altitude(self):
        self.assertAlmostEqual(pressure_altitude_ft_from_station_mb(1013.25), 0.0, places=5)

    def test_millibars_to_inhg(self):
        self.assertAlmostEqual(mb_to_inhg(1013.25), 29.9213, delta=0.001)

    def test_isa_density_altitude(self):
        self.assertAlmostEqual(density_altitude_ft(0, 15), 0, places=3)

    def test_spoken_numbers(self):
        self.assertEqual(speak_digits("2909"), "two niner zero niner")
        self.assertEqual(signed_number_phrase(-9.2), "minus niner")
        self.assertEqual(altimeter_phrase(29.92), "two niner niner two")

    def test_visibility_heuristic(self):
        self.assertEqual(estimate_visibility(20, 19.9, 99), "less than one statute mile")
        self.assertEqual(estimate_visibility(20, 10, 50), "greater than ten statute miles")

    def test_standard_awos_message(self):
        t = datetime.datetime(2026, 11, 16, 18, 45, tzinfo=datetime.timezone.utc)
        s = build_awos_message(24, 63, 1012, station_name="local", when=t)
        self.assertIn("Time one eight four five zulu", s)
        self.assertIn("Wind not available", s)
        self.assertIn("Sky conditions not available", s)
        self.assertIn("Altimeter", s)
        self.assertIn("Density altitude", s)

    def test_extended_format(self):
        t = datetime.datetime(2026, 11, 16, 18, 45, tzinfo=datetime.timezone.utc)
        s = build_extended_awos_message(24, 63, 1012, when=t)
        self.assertIn("Pressure altitude", s)
        self.assertIn("Experimental station", s)
        self.assertIn("Visibility is an experimental humidity based estimate", s)


if __name__ == "__main__":
    unittest.main()
