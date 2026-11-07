# R0A manufacturing review package

**Status: bench prototype.** Review fabrication preview, stock, placement orientation, mechanical fit and intended test scope before order submission.

| File | Contents |
|---|---|
| [Gerber and drill ZIP](GK_CAN_isoSPI_adapter_R0A_prototype_gerbers.zip) | Four copper layers, top paste/silkscreen, both masks, rounded outline and separate plated/non-plated drill files |
| [SMT assembly BOM](bom-jlcpcb-smt.csv) | Exact part IDs and grouped reference designators |
| [SMT placement file](cpl-jlcpcb-smt.csv) | Top-side centroid data in mm with KiCad rotations |
| [Engineering BOM](bom-engineering.csv) | Fitted SMT, THT and separately installed Nano |
| [SHA256SUMS](SHA256SUMS) | CAD and export digests relative to the repository root |

Gerber, drill and CPL use the bottom-left auxiliary origin. The SMT BOM and CPL cover the same 35 parts. Inspect rotation and pin 1 in JLCPCB's PCBA preview. Fit J1–J5 and SW1 through-hole and insert the Arduino module separately. Check the two-transformer supply before quoting assembly.

Design verification reports are under [tests/R0A](../../../tests/R0A/). Electrical bring-up and system insulation qualification remain pending.
