# R0D notes (Nano R4 adapter)

R0D keeps the R0C schematic, placement, outline and copper. A design review on 2026-11-19 added one assembly requirement:

- **Mounting hole H3 takes nylon hardware only.** H3 has no copper, so DRC does not check it, but the hole edge is 6.7 mm from the AUX terminal J5. A metal screw head would reduce that to about 5.5 mm, below the 8 mm isoSPI barrier. The silkscreen next to H3 now reads *H3: NYLON M3 ONLY*. Use a nylon screw, nut and standoff there, or keep metal hardware at least 8 mm from J5.

The Gerber package differs from R0C only in the top silkscreen. The BOM and CPL are unchanged. The [R0D top render](images/board-r0d-top.png) shows the nylon-only marking next to H3.

## Checks

KiCad 10.0.8 reports zero ERC findings and zero DRC, unconnected-item and schematic-parity findings ([reports](../tests/R0D/)). The review also confirmed:

- The ADBMS6822 straps (PHAPOL, XCVRMD and RTO to GND) select SPI mode 0, standard bidirectional mode and a 1.5 s timeout, as the firmware expects. See the [table in the T41-R0B notes](t41-r0b.md#checks), which applies to both boards.
- The Nano 5 V pin sits a diode drop below USB voltage, about 4.4–4.8 V. That is inside the ADBMS6822 VDD range of 3.0–5.5 V.
- The isoSPI domains keep at least 9.2 mm to other copper on every layer.
- R10 = 82 kΩ sets the TPS2553 current limit to about 320 mA.

## Still open

- **ADBMS6822 decoupling.** The capacitors are 4–7 mm from the VDD, VP and VDDS pins. A layout revision should put a 100 nF capacitor at each pin.
- **Insulation class.** Basic insulation only, as described in [decisions](decisions.md#design-review-2026-11-19).
