# Decisions and unresolved release conditions

Updated 2026-11-08. The planning decisions below precede the [R0A prototype implementation](r0a.md); [R0C](r0c.md) is the current Nano R4 revision. The Teensy 4.1 adapter decisions are listed at the end.

## Recorded decisions

- isoSPI is the battery-monitor interface; slave families are ADBMS1818 and ADBMS6832.
- Native MCU USB carries commands and data; the bridge firmware is a bench reference, and application firmware is out of scope.
- Arduino Nano R4 with headers (ABX00143) is the controller baseline.
- Two female sockets and the Nano's own edge-accessible USB-C port are proposed.
- The 1 kV requirement means working voltage. Battery-context interpretation: 1,000 V DC continuous across each isoSPI barrier.
- Select two Bourns SM91801AL-E transformers. Do not substitute a functional-insulation part without reviewing the system requirement.
- Four layers, <100 × 100 mm, predominantly 1206 passives, switchable CAN termination and opposite-edge screw terminals.
- Native KiCad source in a public repository. R0B adds compact placement, diagnostic pads and Nano R4 bench firmware.

## Information and engineering work needed before schematic freeze

| Item | Why it matters | Current disposition |
|---|---|---|
| Exact 6832 suffix/full documentation and both slave schematics | Timing, polarity, magnetics and matching | Public short datasheet is insufficient for full sign-off |
| Cable type, impedance, maximum length and chain size | Link margin and termination | Open |
| Basic vs reinforced insulation, altitude, pollution degree, CTI, transient environment | Board and enclosure insulation coordination | Bourns basic-insulation component selected; system requirement open |
| Maximum actual pack-to-USB voltage including tolerance | 1,000 V is a limit, not extra transient margin | Open |
| CAN-side isolation/fault environment | Isolated DC/DC selection and TVS coordination | Low-voltage CAN network assumed; no 1 kV CAN working claim |
| Exact Nano/socket mechanics and current path | USB access, power droop, retention | Verify physical module and official drawing |
| Sustained logging workload and tolerated loss/host stalls | 32 KB RAM may constrain acquisition | Validate with the application firmware |
| Production quantity and procurement | Two selected transformers required per board; observed stock one | JLCPCB replenishment/preorder/consignment needed |

## Before layout release

Complete schematic ERC, manufacturer pin-by-pin footprint review, power/thermal and insulation calculations, exact passive selection, approved assembly process and connector access review. All unresolved numeric ratings must be resolved or explicitly excluded from the released specification.

## Before fabrication order

Complete DRC, layer-by-layer barrier inspection, enclosure/metal clearance review and BOM/CPL visual cross-check. Recheck stock and reserve enough parts including assembly attrition. Generate fabrication files only from the reviewed PCB revision. Do not label the hardware as tested/certified before the corresponding evidence exists.

## Teensy 4.1 adapter decisions (R0A, 2026-11-08)

- Teensy 4.1 controller, six CAN and six isoSPI ports, 1206 passives, six-layer board, JLCPCB assembly. A four-layer layout left the three ADBMS6822 QFN escapes unroutable; six layers give two ground planes and four routing layers.
- One carrier USB-C for power and data. USB data reaches the Teensy's underside USB device pads through two pogo pins; the Teensy VIN–VUSB pads are cut so power enters only through the carrier fuse and diode.
- CAN1–3 on FlexCAN, CAN4–6 on MCP2518FD. Every CAN port has its own isolated supply, ground, TVS, 120 Ω switch and DSUB-9 female connector wired like PEAK PCAN adapters (CiA 303-1: 2 CAN_L, 7 CAN_H, 3/6 GND).
- Each CAN supply has its own current-limited switch so a fault or an unused port can be switched off. Firmware reads the USB-C CC level and limits a default 500 mA source to two open CAN ports.
- isoSPI uses the same SM91801AL-E transformers and 8 mm copper rule as the Nano adapter.

| Open item | Disposition |
|---|---|
| Teensy USB pad position and D+/D− order | Taken from the PJRC pinout card and an independent footprint; measure a real Teensy 4.1 before ordering |
| Pogo-pin preload and Teensy socket retention | Check with physical parts |
| SM91801AL-E supply, six per board | JLCPCB stock one; pre-order or consign |
| Six-port worst-case current | About 110 mA per transmitting port; confirm on the bench |
| DSUB flange position | 8.10 mm front-row offset read from the Connfly drawing; confirm with a part |
