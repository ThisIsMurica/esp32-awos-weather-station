#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>


// ============================================================
// SENSOR
// ============================================================

// Create our BME280 object.
Adafruit_BME280 bme;




// Send one observation every second.
static const unsigned long SAMPLE_INTERVAL_MS = 1000;


// ============================================================
// SETUP
// ============================================================

void setup() {

  // Start USB serial communication.
  //
  // Python must use the same baud:
  //
  // BAUD = 115200
  //
  Serial.begin(115200);

  delay(1000);


  // Start I2C.
  //
  // This allows the ESP32 to communicate with
  // the onboard BME280.
  Wire.begin(SDA, SCL);


  // Try to find the BME280.
  if (!bme.begin(0x77)) {

    Serial.println("ERROR: BME280 not found at 0x77");

    // Stop here if the sensor isn't available.
    while (1) {
      delay(1000);
    }
  }


  Serial.println("WX station ready.");
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop() {

  // ----------------------------------------------------------
  // READ THE BME280
  // ----------------------------------------------------------

  // Temperature in Celsius.
  float tempC = bme.readTemperature();


  // Relative humidity in percent.
  float rh = bme.readHumidity();


  // BME280 gives pressure in Pascals.
  //
  // 100 Pa = 1 hPa
  //
  // So divide by 100.
  float pressureHpa = bme.readPressure() / 100.0f;


  // ----------------------------------------------------------
  // SEND DATA TO PYTHON
  // ----------------------------------------------------------

  // IMPORTANT:
  //
  // Keep this format because our Python program
  // is specifically looking for:
  //
  // Temp: ...
  // Hum: ...
  // Pres: ...
  //
  // Example:
  //
  // Temp: 24.31 C  Hum: 63.4 %  Pres: 1012.8 hPa
  //

  Serial.print("Temp: ");
  Serial.print(tempC, 2);

  Serial.print(" C  Hum: ");
  Serial.print(rh, 1);

  Serial.print(" %  Pres: ");
  Serial.print(pressureHpa, 1);

  Serial.println(" hPa");


  // Wait one second.
  delay(SAMPLE_INTERVAL_MS);
}