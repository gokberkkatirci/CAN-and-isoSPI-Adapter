# R0B firmware verification

- Arduino CLI 1.5.1, Arduino UNO R4 Boards core 1.6.0, FQBN `arduino:renesas_uno:nanor4`. The sketch compiled using the command in the [flash instructions](../../firmware/README.md), using 59,756 bytes of flash and 6,028 bytes of static RAM.
- A host smoke check using stub Arduino, CAN, SPI and USB interfaces exercised malformed and oversized commands, USB output backpressure, CAN transmit and receive, isoSPI port and payload selection, CAN fault and bus-off handling, and shutdown when the USB session closes.
- No Nano R4 was connected. Upload, physical USB behavior, CAN bit timing and the BMS links remain to be tested on hardware.
