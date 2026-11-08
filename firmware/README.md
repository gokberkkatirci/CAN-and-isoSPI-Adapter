# Firmware

Two USB-serial bridge sketches: [Nano R4 adapter](#nano-r4-adapter) and [Teensy 4.1 adapter](#teensy-41-adapter). Both use the same line-based ASCII protocol style.

## Nano R4 adapter

The sketch in [CanIsoSpiAdapter](CanIsoSpiAdapter/CanIsoSpiAdapter.ino) exposes Classical CAN and raw isoSPI transfers over the Nano R4's native USB serial port. It is intended for bench bring-up on R0A to R0C. It uses the Arduino UNO R4 core's bundled CAN and SPI libraries.

### Build and flash

In Arduino IDE, install **Arduino UNO R4 Boards 1.6.0** in Boards Manager, select **Arduino Nano R4** and the Nano's USB port, open the sketch and select Upload. The [Arduino Nano R4 documentation](https://docs.arduino.cc/hardware/nano-r4/) has board setup and recovery information.

The equivalent Arduino CLI steps from the repository root are:

```sh
arduino-cli core update-index
arduino-cli core install arduino:renesas_uno@1.6.0
arduino-cli board list
arduino-cli compile --fqbn arduino:renesas_uno:nanor4 --output-dir firmware/build firmware/CanIsoSpiAdapter
arduino-cli upload --fqbn arduino:renesas_uno:nanor4 --port YOUR_PORT --input-dir firmware/build firmware/CanIsoSpiAdapter
```

Replace `YOUR_PORT` with the port from `board list`. Use a data-capable USB-C cable. To enter the bootloader if the application port is unavailable, double tap the Nano's reset button and select the bootloader port.

### USB serial commands

Open the port with DTR asserted. Arduino Serial Monitor can use **115200** and **Newline**. USB CDC ignores the numeric baud rate. Send one ASCII command at a time and wait for its `OK` or `ERR` response. Commands are case sensitive. Numbers are decimal unless marked hex.

| Command | Behavior |
|---|---|
| `PING` | Identifies the firmware and reports protocol version 1. |
| `STATUS` | Reports CAN bitrate (zero when closed), latched CAN supply fault, last CAN driver event, and the two channels' raw WAKE and INTR pin levels. |
| `CAN OPEN 500` | Starts CAN at 125, 250, 500, or 1000 kbit/s and enables the isolated CAN supply. This is active CAN and participates in acknowledgement. |
| `CAN TX S 123 AABB` | Queues a standard data frame. Use `X` for extended IDs. ID and data are hex, with up to eight bytes and `-` for zero bytes. `OK QUEUED` confirms submission to the controller. |
| `CAN RX` | Returns `OK RX S 123 AABB` for the next queued data frame, or `OK EMPTY`. Poll often enough for the expected frame rate. |
| `CAN CLOSE` | Disables CAN power and clears queued receive frames. |
| `ISO XFER MAIN 1000000 1 000407C2FFFFFFFFFFFFFFFF` | Selects MAIN or AUX, sets SPI clock in Hz, sends 0–32 wake pulses, and clocks 1–64 hex bytes. The response contains the same number of raw received bytes. |

At reset both isoSPI chip selects are high and CAN power is off. A reported CAN bus-off event, a CAN supply fault, or USB session closure turns CAN power off. Reopen explicitly after resolving the cause. CAN receive buffering is limited by the Arduino core and the USB polling rate. The sketch supports Classical CAN data frames.

isoSPI is SPI mode 0, MSB first. Clock options are 100 kHz, 500 kHz, 1 MHz and 2 MHz. Begin with a low-energy fixture and a short cable. Validate 2 MHz with the actual slave board before use. The example above reads ADBMS1818 cell register group A from a single device. The command and PEC are `000407C2` followed by eight dummy bytes. Discard the four bytes received while sending the command and check the PEC on the remaining register response. The firmware handles the electrical transport. The host supplies command framing and PEC, configures acquisition, and interprets monitor data. [ADBMS1818 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adbms1818.pdf) · [ADBMS6822 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adbms6821-adbms6822.pdf)

### Verification status

Compiled for `arduino:renesas_uno:nanor4` with Arduino CLI 1.5.1 and core 1.6.0. The compiler emitted warnings from the Arduino core and bundled CAN library. No Nano R4 USB port was present during validation, so upload, CAN traffic, and isoSPI timing remain bench checks.

## Teensy 4.1 adapter

[Teensy41CanIsoSpi](Teensy41CanIsoSpi/Teensy41CanIsoSpi.ino) bridges six CAN ports and six isoSPI ports over the Teensy's native USB serial port. CAN1–CAN3 use FlexCAN through the **FlexCAN_T4** library that ships with Teensyduino. CAN4–CAN6 use the MCP2518FD controllers through the **ACAN2517FD** library (Arduino Library Manager). All CAN ports run Classical CAN.

### Build and flash

Install Teensyduino (Teensy board package 1.59 or newer) and the ACAN2517FD library, select **Teensy 4.1** and **USB Type: Serial**, then upload. With Arduino CLI:

```sh
arduino-cli core install teensy:avr --additional-urls https://www.pjrc.com/teensy/package_teensy_index.json
arduino-cli lib install ACAN2517FD
arduino-cli compile --fqbn teensy:avr:teensy41:usb=serial firmware/Teensy41CanIsoSpi
arduino-cli upload --fqbn teensy:avr:teensy41:usb=serial --port YOUR_PORT firmware/Teensy41CanIsoSpi
```

Cut the Teensy's VIN–VUSB pads before first use on the carrier; the carrier USB-C supplies VIN. Program through the carrier USB-C. The Teensy's own micro-USB stays unused.

### USB serial commands

Commands follow the Nano protocol with a channel number added. **Channel N is CAN port N and isoSPI port N**; they sit opposite each other on the board and are numbered 1–6 from left to right with the USB-C connector on the left. When several adapters share a host, tell them apart with `ID` (the unique ID also appears as the USB serial number, so the serial port name stays stable) and an optional `ID SET` label.

| Command | Behavior |
|---|---|
| `PING` | Returns `OK CAN6-ISOSPI6 1`. |
| `ID` | Returns the Teensy's factory-unique 64-bit ID and the stored label, for example `OK ID 1A2B3C4D5E6F7788 LABEL=rack-left`. |
| `ID SET rack-left` | Stores a label of up to 22 letters, digits, `-` or `_` in EEPROM. |
| `MAP` | Lists which controller and isoSPI port belong to channels 1–6. |
| `STATUS` | Bit rate of each CAN port (0 when closed), latched supply fault, USB-C current advertisement read from CC (`DEFAULT`, `1.5A`, `3.0A`), CC voltage and the six isoSPI INTR levels. |
| `CAN OPEN 3 500` | Powers CAN port 3, waits 25 ms, then starts it at 125, 250, 500 or 1000 kbit/s. With a default 500 mA USB source at most two CAN ports open at once; append `FORCE` to override. |
| `CAN TX 3 S 123 AABB` | Queues a standard (`S`) or extended (`X`) data frame on port 3. Hex ID and data, up to eight bytes, `-` for none. |
| `CAN RX 3` | Returns `OK RX 3 S 123 AABB` or `OK EMPTY`. |
| `CAN CLOSE 3` / `CAN CLOSE ALL` | Stops the controller and switches the isolated supply off. |
| `ISO XFER 5 1000000 1 000407C2FFFFFFFFFFFFFFFF` | isoSPI port 5: SPI clock in Hz (100 k, 500 k, 1 M or 2 M), 0–32 wake pulses, 1–64 hex bytes. Returns the raw received bytes. |

The six TPS2553 fault outputs share one line, so a supply fault switches every open CAN port off and latches `FAULT=1` until the next successful `CAN OPEN`. Closing the USB session (DTR low) also switches all CAN supplies off. The green status LED shows that at least one CAN port is open and the red LED shows a supply fault.

### Verification status

The sketch has passed only a host syntax check against stub headers; it has not been built with Teensyduino or run on hardware. See [firmware verification](../tests/T41-R0A/firmware.md).
