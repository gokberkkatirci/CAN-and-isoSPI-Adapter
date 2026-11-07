# R0B prototype notes

R0B reduces the board from 85 × 70 mm to **82 × 64 mm**, about **12% less area**. The Nano and isoSPI assembly moved toward the CAN section, and the isolated CAN converter and rectifier moved up. The screw terminal cable exits, edge USB-C access, and four M3 mounting holes remain available. The compact layout retains four copper layers and the 8 mm copper clearance rule between the floating isoSPI cable domains and other copper.

## Probe points

| Pad | Silkscreen | Signal | Reference |
|---|---|---|---|
| TP1 | USB 5V | Nano header supply | TP2 |
| TP2 | USB GND | Nano and bridge ground | USB domain |
| TP3 | CAN 5V | Isolated regulated CAN supply | TP4 |
| TP4 | CAN GND | Isolated CAN return | CAN domain |
| TP5 | CAN EN | Nano D8, active high converter enable | TP2 |
| TP6 | CAN FLT | Nano A3, active low converter fault | TP2 |

The 1.5 mm probe pads are exposed PCB copper with no solder paste or assembly part. The MAIN/AUX cable domains have no diagnostic probe pads. The board uses the topology and component values described in the [R0A electrical notes](r0a.md).

The checks for this revision cover PCB connectivity, schematic parity, copper clearance, outline size, and a visual review of access to the connectors and probe pads. They do not establish an electrical optimum, measured signal integrity, or a board-level isolation rating. Verify the switching supply startup, CAN waveform and both isoSPI links on the bench before extending the operating envelope.
