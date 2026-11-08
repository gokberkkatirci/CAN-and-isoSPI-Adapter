# Teensy 4.1 adapter firmware verification

- 2026-11-08: the sketch passed a host `clang++ -std=gnu++17 -fsyntax-only -Wall -Wextra` check against small stub headers that model the Teensyduino, FlexCAN_T4, SPI and ACAN2517FD interfaces it uses. This checks C++ syntax and types only. It does not prove that the real library APIs match.
- Not yet done: a Teensyduino build for `teensy:avr:teensy41`, upload through the carrier USB-C and pogo pins, CAN traffic on each port, isoSPI timing and the USB-C CC power-budget reading.
