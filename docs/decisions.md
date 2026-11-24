# Decisions and unresolved release conditions

Updated 2026-11-24. The planning decisions below precede the [R0A prototype implementation](r0a.md); [R0E](r0e.md) is the current Nano R4 revision and [T41-R0C](t41-r0c.md) the current Teensy revision. The Teensy 4.1 adapter decisions are listed at the end.

## Recorded decisions

- isoSPI is the battery-monitor interface; slave families are ADBMS1818 and ADBMS6832.
- Native MCU USB carries commands and data; the bridge firmware is a bench reference, and application firmware is out of scope.
- Arduino Nano R4 with headers (ABX00143) is the controller baseline.
- Two female sockets and the Nano's own edge-accessible USB-C port are proposed.
- The 1 kV requirement means working voltage. Battery-context interpretation: 1,000 V DC continuous across each isoSPI barrier.
- Use isoSPI transformers rated for 1,000 V DC working voltage with basic insulation. The original Bourns SM91801AL-E was replaced in R0E/T41-R0C by the CND-tek HM1238NLTP, which has the same ratings, because JLCPCB had run out of the Bourns part (decision 2026-11-24). Do not substitute a functional-insulation part without reviewing the system requirement.
- Four layers, <100 × 100 mm, predominantly 1206 passives, switchable CAN termination and opposite-edge screw terminals.
- Native KiCad source in a public repository. R0B adds compact placement, diagnostic pads and Nano R4 bench firmware.

## Information and engineering work needed before schematic freeze

| Item | Why it matters | Current disposition |
|---|---|---|
| Exact 6832 suffix/full documentation and both slave schematics | Timing, polarity, magnetics and matching | Public short datasheet is insufficient for full sign-off |
| Cable type, impedance, maximum length and chain size | Link margin and termination | Open |
| Basic vs reinforced insulation, altitude, pollution degree, CTI, transient environment | Board and enclosure insulation coordination | Basic-insulation component selected (HM1238NLTP); system requirement open |
| Maximum actual pack-to-USB voltage including tolerance | 1,000 V is a limit, not extra transient margin | Open |
| CAN-side isolation/fault environment | Isolated DC/DC selection and TVS coordination | Low-voltage CAN network assumed; no 1 kV CAN working claim |
| Exact Nano/socket mechanics and current path | USB access, power droop, retention | Verify physical module and official drawing |
| Sustained logging workload and tolerated loss/host stalls | 32 KB RAM may constrain acquisition | Validate with the application firmware |
| Production quantity and procurement | Every part must be stocked at JLCPCB | All 41 parts in stock on 2026-11-24; EG1218 (139) and ISO1042DWR (206) limit a Teensy order to about 23 boards. See [components](components.md#stock-check-2026-11-24) |

## Before layout release

Complete schematic ERC, manufacturer pin-by-pin footprint review, power/thermal and insulation calculations, exact passive selection, approved assembly process and connector access review. All unresolved numeric ratings must be resolved or explicitly excluded from the released specification.

## Before fabrication order

Complete DRC, layer-by-layer barrier inspection, enclosure/metal clearance review and BOM/CPL visual cross-check. Recheck stock and reserve enough parts including assembly attrition. Generate fabrication files only from the reviewed PCB revision. Do not label the hardware as tested/certified before the corresponding evidence exists.

## Teensy 4.1 adapter decisions (R0A, 2026-11-08)

- Teensy 4.1 controller, six CAN and six isoSPI ports, 1206 passives, six-layer board, JLCPCB assembly. A four-layer layout left the three ADBMS6822 QFN escapes unroutable; six layers give two ground planes and four routing layers.
- One carrier USB-C for power and data. USB data reaches the Teensy's underside USB device pads through two pogo pins. Power enters only through the carrier fuse and diode. R0A cut the Teensy VIN–VUSB pads; R0B keeps them joined, because VUSB powers the Teensy's USB PHY, and forbids using the Teensy micro-USB on the carrier.
- CAN1–3 on FlexCAN, CAN4–6 on MCP2518FD. Every CAN port has its own isolated supply, ground, TVS, 120 Ω switch and DSUB-9 female connector wired like PEAK PCAN adapters (CiA 303-1: 2 CAN_L, 7 CAN_H, 3/6 GND).
- Each CAN supply has its own current-limited switch so a fault or an unused port can be switched off. Firmware reads the USB-C CC level and limits a default 500 mA source to two open CAN ports.
- isoSPI uses the same 1 kV-working, basic-insulation transformers (HM1238NLTP since T41-R0C) and 8 mm copper rule as the Nano adapter.

| Open item | Disposition |
|---|---|
| Teensy USB pad position and D+/D− order | Taken from the PJRC pinout card and an independent footprint; measure a real Teensy 4.1 before ordering |
| Pogo-pin preload, reflow tilt and Teensy socket retention | Check with physical parts; hand-fit J4/J5 if they tilt in reflow |
| isoSPI transformer supply, six per board | Resolved in T41-R0C: HM1238NLTP, 749 in stock on 2026-11-24 |
| Six-port worst-case current | About 110 mA per transmitting port; confirm on the bench |
| DSUB-9 orientation | Vertical (mating face up) Connfly DS1034; confirm fit with a part and the enclosure lid |

## Design review 2026-11-19

Fixed in Teensy [T41-R0B](t41-r0b.md): VUSB supply (pads kept joined), USB D+/D− stubs, VBUS track width. Fixed in Nano [R0D](r0d.md): nylon hardware marked at H3. The ADBMS6822 straps, supply ranges and INTR/WAKE levels were checked against the ADBMS6821/ADBMS6822 datasheet (Rev. B) and are correct on both boards.

| Open item | Disposition |
|---|---|
| Basic vs reinforced insulation | The isoSPI transformer (HM1238NLTP, formerly SM91801AL-E) is basic insulation and the USB side is touchable through the host PC. A product for 1,000 V packs needs reinforced insulation (about 10 mm creepage on the PCB instead of 8 mm) or a second barrier such as a USB isolator. System decision required |
| ADBMS6822 decoupling | Capacitors sit 4–7 mm (Nano) and 6–11 mm (Teensy) from the VDD, VP and VDDS pins; the datasheet asks for at least 1 µF as close as possible to VDD. Add a 100 nF capacitor at each pin in the next layout revision |
| isoSPI termination and filtering | Plain 100 Ω termination. ADI's evaluation board uses a split termination with a capacitor and RC filters on IP/IM; compare EMC margin on the bench |
| Teensy hot-plug capacitance | About 13–17 µF on +5 V, above the USB 10 µF limit; measure inrush |
| Teensy pogo pins | 12 mm pins on a 2 mm SMD pad may tilt in reflow; inspect or fit by hand |
| Teensy net classes | Classes defined in `design.py` are not written to the KiCad project, so a fresh autoroute narrows VBUS again |

## Stock review 2026-11-24 (Nano R0E, Teensy T41-R0C)

JLCPCB no longer stocked three parts, so they were replaced with stocked parts on the same or a similar land pattern. See [components](components.md#changes-for-stock-r0e-t41-r0c).

| Change | Disposition |
|---|---|
| SM91801AL-E → HM1238NLTP | Same 1,000 V DC working rating and basic insulation. Smaller land pattern. Isolation copper rules unchanged, DRC clean |
| 760390014 → MXPP6-3K6110 | Same pinout and land pattern. 1:1.1 instead of 1:1.3, so the CAN LDO runs near dropout. Measure ISO1042 VCC2 while the bus is dominant. MXPP6-3K6130 (1:1.3) is the fallback once its pinout is confirmed |
| TLV76750DGNR → TPS7A1650QDGNRQ1 | Same package and copper. Pin 2 and pin 6 have no internal connection on this part. Rated 100 mA against a 75 mA load |
| HM1238NLTP pin 1 | The drawing has no pin-1 mark. The part is symmetric and fits only one way round; check it in the JLCPCB placement preview |
| EG1218 and ISO1042DWR stock | 139 and 206. ISO1042BDWR (C2671499) is a drop-in second source |
