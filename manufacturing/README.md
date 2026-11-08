# Manufacturing workflow

Prototype exports: [Nano R4 adapter R0C](prototype/R0C/README.md) and [Teensy 4.1 adapter R0A](prototype/T41-R0A/README.md). Each contains draft BOM, CPL, Gerber and drill data from the checked native source. Review stock, PCBA rotations, mechanical fit and the intended test scope before ordering.

## Release sequence

1. Finish source design and verify the selected JLCPCB fabrication stackup and mixed SMT/through-hole assembly service. Confirm whether sockets, terminals and switches are included in the quoted process; install the Nano or Teensy module separately unless explicitly covered.
2. Resolve shortages, especially **SM91801AL-E (two per Nano board, six per Teensy board)**, and all unspecified parts. Recheck exact manufacturer/MPN/C-code, lifecycle, stock, assembly attrition and quantities at order time.
3. Approve ERC, DRC, footprint audit, power/insulation calculations and mechanical fit. Assign a hardware revision and record KiCad version.
4. Export Gerbers, plated/non-plated drill data, schematic PDF, assembly drawings and layer/stackup notes from the same source revision.
5. Export JLCPCB BOM with `Comment`, `Designator`, `Footprint`, `JLCPCB Part #`. Verify the current uploader's accepted columns when exporting. Include one exact purchasable component per grouped line; exclude DNP and separately installed items from the assembly BOM while documenting them in the full engineering BOM.
6. Export CPL/centroid data with `Designator`, `Mid X`, `Mid Y`, `Rotation`, `Layer`; use millimetres and a documented common origin. Review top/bottom transformations and component rotation in JLCPCB's assembly preview. Never invent coordinates in advance.
7. Cross-check every fitted reference between schematic, PCB, BOM and CPL. Resolve pin-1/orientation concerns against assembly drawings, not only the renderer. Clearly identify any THT parts handled outside the SMT centroid workflow.
8. Put approved outputs under `releases/<hardware-revision>/`, add a manifest of source commit/tool version/stackup/options and checksums, and package a fabrication ZIP. Tag the corresponding source revision.

Suggested future package: `gerbers/`, `drill/`, `bom-jlcpcb.csv`, `cpl-jlcpcb.csv`, `bom-engineering.csv`, `schematic.pdf`, `assembly-top.pdf`, `assembly-bottom.pdf`, `fabrication-notes.md`, and `manifest.txt`. Files are intentionally not created as empty manufacturing deliverables.

Official guidance checked during planning: [JLCPCB KiCad BOM/CPL export](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad), [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/), and [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities). Recheck these at release time.
