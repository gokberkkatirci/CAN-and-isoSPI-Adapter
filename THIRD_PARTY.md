# Third-party materials

The adapter uses KiCad 10 standard footprints and standard package models by library reference. KiCad's library license and exception are described on the [KiCad libraries license page](https://www.kicad.org/libraries/license/).

The project-local Carrier symbols, custom land patterns and portable VRML models were created for this adapter from manufacturer drawings. Source links are in [references](docs/references.md) and [model coverage](hardware/kicad/models/README.md). Supplier CAD downloads are kept locally in the ignored vendor directory. This project uses the original Arduino module as a removable part.

The sketch builds against Arduino Renesas UNO core 1.6.0 and its bundled CAN, SPI and USB components. The repository includes the original sketch source. Arduino's compiler, libraries and linked firmware images are built or installed locally. [Arduino Renesas core](https://github.com/arduino/ArduinoCore-renesas/tree/1.6.0)

Repository visibility and permission to reuse the design are separate. The repository owner can select an explicit license for the hardware, firmware, and documentation.
