# Third-party materials

The adapter uses KiCad 10 standard footprints and standard package models by library reference. KiCad's library license and exception are described on the [KiCad libraries license page](https://www.kicad.org/libraries/license/).

The project-local Carrier symbols, custom land patterns and portable VRML models were created for this adapter from manufacturer drawings. Source links are in [references](docs/references.md) and [model coverage](hardware/kicad/models/README.md). Supplier CAD downloads are kept locally in the ignored vendor directory. This project uses the original Arduino module as a removable part.

The sketch builds against Arduino Renesas UNO core 1.6.0 and its bundled CAN, SPI and USB components. The repository includes the original sketch source. Arduino's compiler, libraries and linked firmware images are built or installed locally. [Arduino Renesas core](https://github.com/arduino/ArduinoCore-renesas/tree/1.6.0)

The Teensy 4.1 adapter uses KiCad 10 standard footprints, the four project-local footprints above (copied into `hardware/teensy41/T41Carrier.pretty`) and one new pogo-pin land pattern drawn from the YIYUAN YTC1P-8535-01 listing. Teensy 4.1 pin order and the position of the USB device pads come from the [PJRC Teensy 4.1 pinout cards](https://www.pjrc.com/store/teensy41.html); the pad offsets were cross-checked against the MIT-licensed [teensy.pretty](https://github.com/XenGi/teensy.pretty) footprint. No file from that library is included. The DSUB-9 land pattern was checked against the [Connfly DS1034 drawing](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_CONNFLY-Elec-DS1034-09FUNSi44_C77831.pdf).

The Teensy board was routed with [Freerouting](https://github.com/freerouting/freerouting) (GPL-3.0) through a Specctra round trip. Freerouting is a build tool and is not redistributed. The Teensy sketch builds against Teensyduino, FlexCAN_T4 and [ACAN2517FD](https://github.com/pierremolinaro/acan2517FD) (MIT); none are redistributed.

No reuse license has been selected for this repository yet.
