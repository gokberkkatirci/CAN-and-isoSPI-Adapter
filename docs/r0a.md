# R0A prototype notes

The R0A project uses the socketed Nano R4, an ISO1042DWR CAN transceiver, a dual ADBMS6822 and two SM91801AL-E transformers. The 85 × 70 mm outline has four 3.2 mm mounting holes and opposite-edge screw terminals. Local custom symbols and footprints ship with the project.

D8 switches only the CAN power converter. VDDS, VDD and VP of the ADBMS6822 are tied to the Nano's 5 V rail, with separate local bypass capacitors. CAN has its own rectified and regulated 5 V bus rail. R10 is 82 kΩ, giving a nominal TPS2553 threshold near 324 mA using the [TI datasheet equations](https://www.ti.com/lit/ds/symlink/tps2553.pdf). This threshold applies to the switched CAN converter branch. Check startup, Nano supply loading and USB current in the actual assembly.

R3/R4 are initial 100 Ω differential terminations at the transformer primaries. Verify matching, return timing and error rate with the selected twisted pairs and both battery-monitor chains. The [ADI reference schematic](https://www.analog.com/media/en/technical-documentation/eval-board-schematic/eval-adbms6822-schematic.pdf) uses a different magnetics and matching arrangement. R0A uses ordinary bidirectional mode and starts bring-up at or below 1 Mbit/s.

KiCad 10.0.6 schematic ERC and PCB DRC with schematic parity were run on 2026-11-07. Both returned zero findings, including zero unconnected items. DRC includes 8 mm clearance between each floating isoSPI cable domain and copper outside that domain. Physical fit, pulse response, power margins, connector access, insulation coordination and manufacturing preview remain verification tasks.

The PCB uses 0.15 mm ordinary copper clearance and a 0.18 mm minimum trace width, with 0.60/0.30 mm nominal vias. Confirm the final fabrication options and laminate with the board house. The 1 kV DC transformer rating applies to the selected component under its specified conditions. System qualification requires separate board and enclosure review.
