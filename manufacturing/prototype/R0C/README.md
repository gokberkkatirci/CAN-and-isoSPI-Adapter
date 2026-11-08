# Nano R4 adapter R0C manufacturing files

**Status: bench prototype.** Review the fabrication preview, stock, placement orientation and mechanical fit before ordering.

| File | Contents |
|---|---|
| [Gerber and drill ZIP](CAN_isoSPI_adapter_R0C_prototype_gerbers.zip) | Four copper layers, top paste and silkscreen, both masks, rounded outline, separate plated and non-plated drill files |
| [SMT assembly BOM](bom-jlcpcb-smt.csv) | JLCPCB part numbers and grouped designators |
| [SMT placement file](cpl-jlcpcb-smt.csv) | Top-side centroids in mm with KiCad rotations |
| [Engineering BOM](bom-engineering.csv) | Fitted SMT and THT parts and the separately installed Nano |
| [SHA256SUMS](SHA256SUMS) | Digests of the CAD source and exports, relative to the repository root |

Gerber, drill and CPL use the bottom-left auxiliary origin. The SMT BOM and CPL cover the same 35 parts. The six test pads are bare copper with no paste or assembly entry. Fit J1–J5 and SW1 as through-hole parts and insert the Arduino module separately.

JLCPCB stock checked 2026-11-08: every part is listed in stock except **SM91801AL-E (C26423704), which showed one unit**. Each board needs two. Check the rotation and pin 1 of every part in JLCPCB's PCBA preview.
