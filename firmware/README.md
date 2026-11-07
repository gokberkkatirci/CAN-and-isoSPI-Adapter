# Nano R4 adapter firmware

The sketch in [CanIsoSpiAdapter](CanIsoSpiAdapter/CanIsoSpiAdapter.ino) exposes Classical CAN and raw isoSPI transfers over the Nano R4's native USB serial port. It is intended for bench bring-up on R0A and R0B. It uses the Arduino UNO R4 core's bundled CAN and SPI libraries.

## Build and flash

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

## USB serial commands

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

## Verification status

Compiled for `arduino:renesas_uno:nanor4` with Arduino CLI 1.5.1 and core 1.6.0. The compiler emitted warnings from the Arduino core and bundled CAN library. No Nano R4 USB port was present during validation, so upload, CAN traffic, and isoSPI timing remain bench checks.
