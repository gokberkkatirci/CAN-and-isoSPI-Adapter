# Mechanical planning

R0B layout: **82 × 64 mm**, four layers, nominal 1.6 mm thickness, rounded corners and four M3 mounting holes. The six diagnostic pads are outside the Nano footprint. Isolation spacing takes precedence over further outline reduction.

CAN terminal: left edge. MAIN/AUX isoSPI terminals: right edge, with separation between their isolated cable domains. Nano R4 USB-C: front edge. Keep terminal screws, reset/boot access and module removal accessible. Use two black 1×15 female sockets on a 2.54 mm pin grid; verify row spacing, engagement height and every pad against the official mechanical drawing and a physical ABX00143 before footprint approval. Keep the underside clear of tall components. Add mechanical support so USB cable forces do not rely solely on socket friction. Check module USB plug clearance, mounting holes and enclosure clearance before fixing the outline.

Any connector that mates to a separate existing main board requires that board's pinout and mechanical drawing. No existing-board compatibility is claimed.
