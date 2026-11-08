# Teensy 4.1 adapter — User manual

This manual covers assembly, firmware installation, and everyday use of the six-CAN / six-isoSPI Teensy 4.1 adapter board (CAN6_isoSPI6_T41 R0A).

## 1  Board overview

The adapter has 216 × 120 mm, six layers, and is designed around a socketed Teensy 4.1. A single USB-C connector on the left edge provides both power and USB data.

- **Bottom edge:** six vertical DSUB-9 female connectors (CAN1 through CAN6, left to right). Each has a 120 Ω termination switch and a green power LED.
- **Top edge:** six isoSPI terminals (isoSPI 1 through isoSPI 6), each directly opposite the CAN port with the same number. The **+** terminal is on the left of each pair.
- **Centre:** Teensy 4.1 in two 1 × 24 pin sockets. USB end faces left toward the USB-C connector.

**Channel N** is one column of the board: CAN N (bottom) and isoSPI N (top).

## 2  Assembly

### 2.1  Before soldering

If ordering from JLCPCB, SMT parts are placed by the assembly service. The through-hole parts (six DSUB-9 connectors, six EG1218 slide switches, six isoSPI terminals, and the two 1 × 24 Teensy sockets) are hand-soldered after the boards arrive.

### 2.2  Teensy preparation

**Cut the VIN–VUSB pads** on the Teensy 4.1 underside before inserting it. The carrier board feeds VIN through the PTC fuse and Schottky diode. Leaving the pads joined will back-feed the carrier's VBUS to the Teensy's micro-USB VBUS pin. See the [Teensy 4.1 documentation](https://www.pjrc.com/store/teensy41.html#power) for the pad location.

### 2.3  Inserting the Teensy

Place the Teensy with its USB connector end pointing left (toward the carrier USB-C). The pin headers drop into sockets J2 (top row) and J3 (bottom row). Do not press the Teensy's own micro-USB connector into anything — the carrier's pogo pins J4 and J5 press onto the Teensy's underside USB device pads for data.

### 2.4  Pogo pin alignment check

Before final assembly, measure the D−/D+ pad positions on your Teensy against J4 and J5 on the carrier. The pogo pads are at Teensy column 1 + 0.73 mm, centred ±1.27 mm from the Teensy midline. A misalignment here means no USB enumeration.

## 3  Flashing the firmware

### 3.1  Requirements

- [Teensyduino](https://www.pjrc.com/teensy/td_download.html) (board package 1.59 or newer)
- **ACAN2517FD** library (Arduino Library Manager or [GitHub](https://github.com/pierremolinaro/acan2517FD))
- A data-capable USB-C cable

### 3.2  Using Arduino IDE

1. Install Teensyduino and the ACAN2517FD library.
2. Open `firmware/Teensy41CanIsoSpi/Teensy41CanIsoSpi.ino`.
3. Select **Tools → Board → Teensy 4.1**.
4. Set **Tools → USB Type → Serial**.
5. Select the Teensy's serial port under **Tools → Port**.
6. Click **Upload**.

### 3.3  Using Arduino CLI

```sh
# Install Teensy board package
arduino-cli core install teensy:avr \
  --additional-urls https://www.pjrc.com/teensy/package_teensy_index.json

# Install the MCP2518FD library
arduino-cli lib install ACAN2517FD

# Compile
arduino-cli compile --fqbn teensy:avr:teensy41:usb=serial \
  firmware/Teensy41CanIsoSpi

# Upload (replace YOUR_PORT with the actual serial port)
arduino-cli upload --fqbn teensy:avr:teensy41:usb=serial \
  --port YOUR_PORT firmware/Teensy41CanIsoSpi
```

### 3.4  First boot check

After flashing, open the serial port at 115200 baud with DTR asserted (Arduino Serial Monitor works). Send:

```
PING
```

Expected response:

```
OK CAN6-ISOSPI6 1
```

## 4  Connecting the hardware

### 4.1  CAN bus wiring

Each DSUB-9 connector uses the CiA 303-1 (PEAK PCAN) pinout:

| Pin | Signal |
|-----|--------|
| 2   | CAN_L  |
| 7   | CAN_H  |
| 3, 6 | Isolated CAN ground |
| 5, shell | Shield (to CAN ground through 1 MΩ ∥ 4.7 nF) |

Standard CAN cables and termination plugs work directly. Set the channel's slide switch to **120R** if this adapter terminates an end of that CAN bus, or **OFF** otherwise.

### 4.2  isoSPI wiring

Each isoSPI terminal is a two-wire differential pair. Use a twisted pair cable. The **+** terminal is on the left of each pair (viewed from the component side). Connect to the corresponding isoSPI port on the battery monitor daisy-chain.

### 4.3  Power

The carrier draws power from USB-C VBUS (5 V). Each CAN port consumes roughly 110 mA when transmitting. The Teensy, isoSPI bridges and controllers use about 250 mA.

| USB source | Ports you can open |
|---|---|
| Default USB 2.0 (500 mA) | Up to 2 CAN ports |
| USB-C 1.5 A | Up to 6 CAN ports |
| USB-C 3.0 A | Up to 6 CAN ports |

The firmware reads the USB-C CC pins to detect the source's current advertisement and blocks additional ports when the budget is exceeded. Append `FORCE` to `CAN OPEN` to override.

## 5  USB serial command reference

Open the port with DTR asserted. Send one ASCII command per line and wait for its `OK` or `ERR` response. Commands are case sensitive. Numbers are decimal unless noted as hex.

### 5.1  System commands

| Command | Response | Description |
|---|---|---|
| `PING` | `OK CAN6-ISOSPI6 1` | Identify the adapter and protocol version |
| `ID` | `OK ID 1A2B3C4D5E6F7788 LABEL=my-adapter` | Report factory-unique 64-bit ID and stored label |
| `ID SET my-adapter` | `OK ID …` | Store a label (up to 22 chars: A–Z, a–z, 0–9, `-`, `_`) in EEPROM |
| `MAP` | `OK MAP CH1=FLEXCAN1,ISO1 …` | Show which controller drives each channel |
| `STATUS` | `OK STATUS CAN=… FAULT=… USB=… CC=… ISO_INTR=…` | Full system status |

### 5.2  CAN commands

**Open a CAN port:**

```
CAN OPEN <channel> <bitrate>
```

- `channel`: 1–6
- `bitrate`: 125, 250, 500 or 1000 (kbit/s)

Example: `CAN OPEN 1 500` → `OK CAN1 500 ACTIVE`

The isolated power supply is switched on and the transceiver starts. Add `FORCE` at the end to ignore the USB power budget check.

**Send a CAN frame:**

```
CAN TX <channel> <format> <id> <data>
```

- `format`: `S` (standard 11-bit) or `X` (extended 29-bit)
- `id`: hex, up to 7FF (standard) or 1FFFFFFF (extended)
- `data`: hex bytes (up to 8 bytes), or `-` for a remote/empty frame

Examples:

```
CAN TX 1 S 123 AABBCCDD
CAN TX 3 X 18DAF110 0102030405060708
CAN TX 2 S 7DF -
```

**Receive a CAN frame:**

```
CAN RX <channel>
```

Returns `OK RX <channel> <format> <id> <data>` or `OK EMPTY`. Poll at a rate matching the expected bus traffic.

Example: `CAN RX 1` → `OK RX 1 S 123 AABBCCDD`

**Close a CAN port:**

```
CAN CLOSE <channel>
CAN CLOSE ALL
```

Stops the controller, switches off the isolated supply, and clears receive buffers.

### 5.3  isoSPI commands

**Transfer data on an isoSPI port:**

```
ISO XFER <port> <clock> <wakes> <hex_bytes>
```

- `port`: 1–6
- `clock`: SPI clock in Hz — 100000, 500000, 1000000 or 2000000
- `wakes`: number of wake-up pulses to send first (0–32)
- `hex_bytes`: 1–64 bytes as a hex string

Example — read ADBMS1818 cell register group A from a single device on port 5:

```
ISO XFER 5 1000000 1 000407C2FFFFFFFFFFFFFFFF
```

Response: `OK ISO 5 <received_hex_bytes>`

The firmware handles the electrical transport (SPI, chip select, wake pulses). The host is responsible for command framing, PEC computation and interpretation of the monitor data. See the [ADBMS1818 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adbms1818.pdf) for command encoding.

## 6  Channel assignment

Channels 1–6 run left to right. Each column is independent:

| Channel | CAN controller | isoSPI bridge | Notes |
|---|---|---|---|
| 1 | FlexCAN1 | ADBMS6822 U701 ch2 | |
| 2 | FlexCAN2 | ADBMS6822 U701 ch1 | |
| 3 | FlexCAN3 (CAN FD capable) | ADBMS6822 U801 ch2 | |
| 4 | MCP2518FD U405 | ADBMS6822 U801 ch1 | |
| 5 | MCP2518FD U505 | ADBMS6822 U901 ch2 | |
| 6 | MCP2518FD U605 | ADBMS6822 U901 ch1 | |

Send `MAP` at the serial port to confirm this on a live adapter.

### 6.1  Identifying multiple adapters

Each Teensy 4.1 has a factory-programmed unique 64-bit ID (OCOTP MAC fuses). Use `ID` to read it. The same ID appears as the USB serial number, so the operating system assigns the same port name across reboots.

To assign a human-readable name:

```
ID SET rack-left
```

Read it back:

```
ID
OK ID 1A2B3C4D5E6F7788 LABEL=rack-left
```

## 7  Typical workflows

### 7.1  Sniffing a CAN bus

```
CAN OPEN 1 500
CAN RX 1            (repeat / poll)
CAN CLOSE 1
```

### 7.2  Sending a UDS diagnostic request

```
CAN OPEN 2 500
CAN TX 2 S 7DF 0201050000000000
CAN RX 2
CAN CLOSE 2
```

### 7.3  Reading battery monitor cells over isoSPI

```
ISO XFER 3 1000000 2 000407C2FFFFFFFFFFFFFFFF
```

Two wake pulses bring the daisy-chain out of sleep. The command bytes `000407C2` are the ADBMS1818 RDCVA command with PEC. The eight `FF` bytes clock the response. Parse the returned bytes according to the data sheet.

### 7.4  Multi-bus bridge

Open several CAN ports and relay frames between them:

```
CAN OPEN 1 500
CAN OPEN 4 250
CAN RX 1          → if a frame arrives, send it on port 4:
CAN TX 4 S <id> <data>
```

## 8  Test points

The board has 16 test points (1.5 mm pads) accessible with a scope or multimeter:

| Label | Net | Location |
|---|---|---|
| 5V | +5V rail | Left group, row 1 |
| GND | Ground | Left group, row 1 |
| 3V3 | +3.3V rail | Left group, row 1 |
| VBUS | USB VBUS | Left group, row 1 |
| FLT | CAN power fault (active low) | Left group, row 2 |
| D32 | Teensy pin 32 (spare) | Left group, row 2 |
| D+ | USB D+ | Left group, row 2 |
| D- | USB D- | Left group, row 2 |
| MOSI | isoSPI SPI MOSI | Right group, row 1 |
| MISO | isoSPI SPI MISO | Right group, row 1 |
| SCK | isoSPI SPI SCK | Right group, row 1 |
| TX1 | CAN1 TX (FlexCAN1) | Right group, row 1 |
| RX1 | CAN1 RX (FlexCAN1) | Right group, row 1 |
| MOSI1 | MCP2518FD SPI1 MOSI | Right group, row 2 |
| MISO1 | MCP2518FD SPI1 MISO | Right group, row 2 |
| SCK1 | MCP2518FD SPI1 SCK | Right group, row 2 |

## 9  LED indicators

| LED | Color | Meaning |
|---|---|---|
| 5V LED (near USB-C) | Green | +5V rail is live |
| OK LED | Green | At least one CAN port is open |
| ERR LED | Red | A TPS2553 supply fault is latched |
| CAN port LEDs (×6) | Green | That port's isolated 5V supply is on |

## 10  Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No USB enumeration | VIN–VUSB pads not cut; pogo pin misalignment | Cut the Teensy pads; check J4/J5 alignment |
| `ERR usb-power-budget` | Default USB source, >2 ports open | Use a 1.5 A or 3 A USB-C source, or add `FORCE` |
| `ERR can-power-fault` | Short or overcurrent on the isolated supply | Check CAN wiring; the TPS2553 current limit is ~200 mA |
| `ERR can-init 0x…` | MCP2518FD failed to start | Check SPI1 connections; the error code is from the ACAN2517FD library |
| ERR LED stays on | Supply fault latched | Close all ports, fix the cause, then reopen |
| `OK EMPTY` on `CAN RX` | No frames in buffer | Check bus wiring, termination, and that another node is transmitting |
| isoSPI returns all zeros | Cable disconnected or wrong polarity | Check twisted pair and +/− orientation |
| isoSPI returns all FF | No response from the monitor | Send wake pulses (increase the third argument); check daisy-chain power |

## 11  Safety notes

- This is a bench prototype. Board creepage, insulation coordination and enclosure clearances have not been certified.
- The CAN isolation is intended for low-voltage CAN networks.
- The isoSPI transformer working voltage is rated 1 kV DC (basic insulation). Do not rely on this for safety isolation.
- Always verify the CAN bus termination (120 Ω on both ends) before connecting the adapter to a live bus.
