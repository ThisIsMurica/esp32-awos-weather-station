# DECtalk and third-party dependencies

The source project uses a Windows DECtalk speech runtime through `ctypes` and depends on Flask, pyserial, and the Adafruit BME280 firmware libraries.

This public repository **does not redistribute** DECtalk DLLs, EXE files, speech dictionaries, license configuration or pre-generated recordings. Install and configure the runtime locally if your version and license permit use.

DECtalk voices, binaries, and dictionaries are third-party resources. Their availability and redistribution terms are separate from this project's original ESP32 and Python application code.

The source archive also included standalone DECtalk experiment scripts, a pyttsx3 voice-enumeration experiment, and a sample generated WAV. They were not included in the primary reproducible application to keep the portfolio focused on the working data-to-audio pipeline.
