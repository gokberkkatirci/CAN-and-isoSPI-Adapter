# Teensy 4.1 adapter R0A manufacturing files (JLCPCB)

**Status: bench prototype.** Review the fabrication preview, stock, placement orientation and mechanical fit before ordering.

| File | Contents |
|---|---|
| [Gerber and drill ZIP](CAN6_isoSPI6_T41_R0A_gerbers.zip) | Six copper layers, top paste and silkscreen, both masks, rounded outline, separate plated and non-plated drill files |
| [JLCPCB BOM](bom-jlcpcb.csv) | `Comment`, `Designator`, `Footprint`, `JLCPCB Part #`; 36 lines, 254 placements, SMT and through-hole |
| [JLCPCB placement (CPL)](cpl-jlcpcb.csv) | `Designator`, `Mid X`, `Mid Y`, `Rotation`, `Layer`; centre of each part's pad field, in millimetres from the bottom-left board corner |
| [Engineering BOM](bom-engineering.csv) | Every fitted part with manufacturer, MPN and assembly type, plus the separately bought Teensy |
| [SHA256SUMS](SHA256SUMS) | Digests of the CAD source and exports, relative to the repository root |

All components are on the top side. Through-hole parts (DSUB-9 ×6, EG1218 ×6, isoSPI terminals ×6, Teensy sockets ×2) are in the BOM and CPL so JLCPCB can quote them for through-hole assembly; drop them from both files to fit them by hand. Test pads and mounting holes have no assembly entry. The Teensy 4.1 is bought separately; cut its VIN–VUSB pads before inserting it.

Order options: 6 layers, 1.6 mm, 216 × 120 mm, 1 oz outer copper, minimum track 0.1 mm (short neck-downs at fine-pitch pads), 0.3 mm vias, HASL or ENIG. ENIG gives the pogo-pin pads a flatter, more durable surface.

Rotations are KiCad footprint rotations. Check every polarized part in JLCPCB's placement preview (pin 1 of ICs, LED and diode cathodes, crystal and USB-C orientation) and correct rotations there if needed.

JLCPCB stock checked 2026-11-08 is listed in [components](../../../docs/components.md#teensy-41-adapter-r0a). **SM91801AL-E (C26423704) showed one unit; six are needed per board.** ISO1042DWR (128) and 760390014 (214) cover about 20 and 35 boards.
