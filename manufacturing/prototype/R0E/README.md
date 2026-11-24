# Nano R4 adapter R0E manufacturing files (JLCPCB)

**Status: lab prototype, ready to order.** All SMT and through-hole parts with a JLCPCB code were in stock on 2026-11-24 ([stock list](../../../docs/components.md#stock-check-2026-11-24)). Recheck stock in the quote, and check rotations in the placement preview before you confirm.

| File | Contents |
|---|---|
| [Gerber and drill ZIP](CAN_isoSPI_adapter_R0E_prototype_gerbers.zip) | Four copper layers, top paste and silkscreen, both masks, rounded outline, separate plated and non-plated drill files |
| [SMT assembly BOM](bom-jlcpcb-smt.csv) | JLCPCB part numbers and grouped designators; 16 lines |
| [SMT placement file](cpl-jlcpcb-smt.csv) | Top-side footprint origins in mm from the bottom-left auxiliary origin, with KiCad rotations; 35 parts |
| [Engineering BOM](bom-engineering.csv) | Fitted SMT and THT parts and the separately installed Nano |
| [SHA256SUMS](SHA256SUMS) | Digests of the CAD source and exports, relative to the repository root |

## Ordering at JLCPCB

1. Upload the Gerber ZIP. Choose 4 layers, 1.6 mm, 82 × 64 mm, 1 oz outer copper and HASL or ENIG. The smallest track is 0.2 mm and the vias are 0.6/0.3 mm.
2. Choose PCB assembly, top side. Upload `bom-jlcpcb-smt.csv` and `cpl-jlcpcb-smt.csv`.
3. In the placement preview, check pin 1 of every IC and the cathode of every diode. Check the HM1238NLTP (T1, T2): its drawing has no pin-1 mark, and its uneven lead pitch fits only one way round, with the two leads 2.54 mm apart toward the bottom of the board in both rows (pin 1 is the upper-left lead). Correct a rotation there if a part is drawn turned.
4. Fit J1–J5 and SW1 by hand as through-hole parts. J3–J5 and SW1 have JLCPCB codes in the engineering BOM if you would rather add them to the assembly order. The Nano sockets J1/J2 (SSW-115-01-G-S) have no JLCPCB code.
5. Insert the Arduino Nano R4 (ABX00143) separately. **Mount H3 with nylon M3 hardware only**: it is 6.7 mm from the AUX terminal ([R0D notes](../../../docs/r0d.md)).

The six test pads are bare copper with no paste or assembly entry.

## Changes from R0D

R0E replaces three parts that JLCPCB no longer stocked ([R0E notes](../../../docs/r0e.md)):

| Ref | R0D | R0E |
|---|---|---|
| T1, T2 | SM91801AL-E (C26423704) | HM1238NLTP (C49230397) |
| T3 | 760390014 (C2802211) | MXPP6-3K6110 (C19943838) |
| U5 | TLV76750DGNR (C3752807) | TPS7A1650QDGNRQ1 (C2832237) |

In the CPL, only T1 and T2 moved. In the Gerbers, the outline, B.Mask and NPTH drill file are unchanged. The PTH drill file has five more vias.
