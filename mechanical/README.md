# Mechanical planning

Nano R4 adapter (R0B/R0C layout): **82 × 64 mm**, four layers, nominal 1.6 mm thickness, rounded corners and four M3 mounting holes. The six diagnostic pads are outside the Nano footprint. Isolation spacing takes precedence over further outline reduction.

CAN terminal: left edge. MAIN/AUX isoSPI terminals: right edge, with separation between their isolated cable domains. Nano R4 USB-C: front edge. Keep terminal screws, reset/boot access and module removal accessible. Use two black 1×15 female sockets on a 2.54 mm pin grid; verify row spacing, engagement height and every pad against the official mechanical drawing and a physical ABX00143 before footprint approval. Keep the underside clear of tall components. Add mechanical support so USB cable forces do not rely solely on socket friction. Check module USB plug clearance, mounting holes and enclosure clearance before fixing the outline.

No board-to-board mating connector is defined.

Teensy 4.1 adapter (R0A): **216 × 120 mm**, six layers, 1.6 mm, six M3 holes. Six vertical DSUB-9 connectors sit along the bottom edge (33 mm pitch, mating faces up, so the enclosure lid needs six DSUB cut-outs) and six isoSPI terminals the top edge. The Teensy sits 11 mm above the carrier on 8.5 mm sockets; the two pogo pins under its USB end need that height. USB-C is on the left edge next to the Teensy's USB end. Check the DSUB positions against the Connfly DS1034 drawing and a physical part before lid cut-outs are made.
