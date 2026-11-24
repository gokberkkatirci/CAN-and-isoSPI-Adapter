# Teensy 4.1 adapter T41-R0C manufacturing files (JLCPCB)

**Status: lab prototype, ready to order.** All 36 BOM lines were in stock at JLCPCB on 2026-11-24 ([stock list](../../../docs/components.md#stock-check-2026-11-24)). Recheck stock in the quote, and check rotations in the placement preview before you confirm.

| File | Contents |
|---|---|
| [Gerber and drill ZIP](CAN6_isoSPI6_T41_R0C_gerbers.zip) | Six copper layers, top paste and silkscreen, both masks, rounded outline, separate plated and non-plated drill files |
| [JLCPCB BOM](bom-jlcpcb.csv) | `Comment`, `Designator`, `Footprint`, `JLCPCB Part #`; 36 lines, 254 placements, SMT and through-hole |
| [JLCPCB placement (CPL)](cpl-jlcpcb.csv) | `Designator`, `Mid X`, `Mid Y`, `Rotation`, `Layer`; centre of each part's pad field, in millimetres from the bottom-left board corner |
| [Engineering BOM](bom-engineering.csv) | Every fitted part with manufacturer, MPN and assembly type, plus the separately bought Teensy |
| [SHA256SUMS](SHA256SUMS) | Digests of the CAD source and exports, relative to the repository root |

## Ordering at JLCPCB

1. Upload the Gerber ZIP. Choose 6 layers, 1.6 mm, 216 × 120 mm, 1 oz outer copper and HASL or ENIG. ENIG gives the pogo-pin pads a flatter, more durable surface. The smallest track is 0.12 mm (short neck-downs at fine-pitch pads) and the vias are 0.6/0.3 mm.
2. Choose PCB assembly, top side. Upload `bom-jlcpcb.csv` and `cpl-jlcpcb.csv`.
3. In the placement preview, check pin 1 of every IC and the cathode of every LED and diode, as well as the crystal, USB-C and transformer orientation. Correct a rotation there if a part is drawn turned. The rotations are KiCad footprint rotations.
4. The HM1238NLTP (T701–T902) has no pin-1 mark on its drawing. Its uneven lead pitch fits only one way round: in both lead rows, the two leads 2.54 mm apart are on the right (pin 1 is the lower-left lead).
5. Through-hole parts (DSUB-9 ×6, EG1218 ×6, isoSPI terminals ×6, Teensy sockets ×2) are in the BOM and CPL, so JLCPCB can quote through-hole assembly. To fit them by hand, delete them from both files.
6. Buy the Teensy 4.1 with pins separately and keep its VIN–VUSB pads joined.

The pogo pins J4/J5 are 12 mm tall on a 2 mm SMD pad and may tilt in reflow. Check them in the placement preview and after assembly. Alternatively, delete J4 and J5 from both files and solder them by hand, with a Teensy fitted in the sockets as an alignment jig.

Test pads and mounting holes have no assembly entry.

## Changes from R0B

R0C replaces three parts that JLCPCB no longer stocked ([T41-R0C notes](../../../docs/t41-r0c.md)):

| Refs | R0B | R0C |
|---|---|---|
| T701–T902 | SM91801AL-E (C26423704) | HM1238NLTP (C49230397) |
| T101–T601 | 760390014 (C2802211) | MXPP6-3K6110 (C19943838) |
| U104–U604 | TLV76750DGNR (C3752807) | TPS7A1650QDGNRQ1 (C2832237) |

In the CPL, only T701–T902 moved. The Gerbers differ from R0B only in the copper, paste, mask and silkscreen around these parts. The outline, B.Mask and both drill files are unchanged.

The scarcest parts are EG1218 (139, about 23 boards) and ISO1042DWR (206, about 34 boards). For a larger order, add ISO1042BDWR (C2671499) as a second source.
