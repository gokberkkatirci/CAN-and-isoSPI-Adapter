# Component selection and sourcing

**Planning shortlist, not a production BOM.** JLCPCB quantities below were observed in its live parts-library UI on **2026-11-07**, approximately 09:08–09:20 Europe/Berlin; the selected Bourns transformer was rechecked later the same session and still showed one. These are availability snapshots, not reservations or supplier commitments. Technical specifications come from the manufacturer references, not marketplace descriptions.

| Function | Manufacturer / exact MPN | Qty per board | JLCPCB code | Observed stock | Disposition |
|---|---|---:|---|---:|---|
| Socketed controller | Arduino ABX00143 | 1 | Not verified | — | Selected; buy module separately |
| Dual isoSPI bridge | Analog Devices ADBMS6822WCCSZ-RL | 1 | [C19190031](https://jlcpcb.com/partdetail/C19190031) | 5,136 | Selected architecture; verify exact footprint |
| isoSPI transformers | Bourns SM91801AL-E | 2 | [C26423704](https://jlcpcb.com/partdetail/C26423704) | **1** | **Selected for 1,000 V DC working/basic insulation; sourcing shortage** |
| Isolated CAN transceiver | Texas Instruments ISO1042DWR | 1 | [C1848126](https://jlcpcb.com/partdetail/C1848126) | 132 | Selected architecture |
| Isolated supply driver | Texas Instruments SN6505BDBVR | 1 | [C74518](https://jlcpcb.com/partdetail/C74518) | 1,288 | Candidate pending power calculation |
| CAN power transformer | Würth Elektronik 760390014 | 1 | [C2802211](https://jlcpcb.com/partdetail/C2802211) | 420 | Candidate; no 1 kV continuous CAN rating established |
| CAN supply regulator | Texas Instruments TLV76750DGNR | 1 | [C3752807](https://jlcpcb.com/partdetail/C3752807) | 1,033 | Candidate; verify headroom/thermal limits |
| Carrier current limiter | Texas Instruments TPS2553DBVR | 1 | [C55266](https://jlcpcb.com/partdetail/C55266) | 58,076 | Candidate; calculate current-setting resistor |
| CAN TVS | Nexperia PESD2CANFD24V-TR | 1 | [C552486](https://jlcpcb.com/partdetail/C552486) | 18,218 | Candidate; fault coordination required |
| CAN screw terminal | Phoenix Contact 1715734 | 1 | [C480520](https://jlcpcb.com/partdetail/C480520) | 1,204 | 3 positions, through-hole |
| isoSPI screw terminals | Phoenix Contact 1715721 | 2 | [C480516](https://jlcpcb.com/partdetail/C480516) | 2,522 | Separate 2-position bodies |
| Termination switch | E-Switch EG1218 | 1 | [C273394](https://jlcpcb.com/partdetail/C273394) | 1,414 | Candidate; drawing/contact review required |
| 240 Ω termination resistors | UNI-ROYAL 1206W4F2400T5E | 2 | [C17961](https://jlcpcb.com/partdetail/C17961) | 31,408 | Parallel pair gives 120 Ω; validate derating |

Listed JLC parts were marked Extended. Assembly fees, minimum quantities and attrition are quote-dependent. Use exact manufacturer/MPN/C-code combinations: matching an MPN text alone can select a different manufacturer.

## Selected transformer

**SM91801AL-E**, two per board: 1:1 ratio, single channel, SMT, approximately 14 × 8.5 × 5.5 mm. Manufacturer specifies up to 1,000 V DC working voltage, basic insulation, and separate hipot ratings of 4,300 V DC / 2,500 V AC [manufacturer datasheet](https://www.bourns.com/docs/product-datasheets/sm91801al.pdf). Validate electrical compatibility and the final matching network with ADBMS6822 and both slave-board implementations; this is not a claim of an ADI-qualified combination.

Stock one is insufficient for even one two-port assembly. Before ordering, obtain replenishment or an accepted JLCPCB preorder/consigned supply; do not create an order-ready BOM claiming all-stock availability. Do not change the transformer to resolve stock without reviewing insulation, pulse response and footprint again.

## Alternatives not in the baseline

- Pulse HM2101NLT, [C5718397](https://jlcpcb.com/partdetail/C5718397), observed stock 1,026: its manufacturer lists 1 kV working voltage but **functional** insulation. Not approved as a replacement for the Bourns basic-insulation selection.
- LTC6820: useful for 1 Mbit/s designs but not the preferred bridge for the requested 6832 capability.
- ISOW1044 integrated isolated-power CAN: observed procurement/cost was unattractive; no selection made.
- A separate carrier USB-C receptacle/USB bridge is unnecessary when using the Nano's own USB-C port.

## Parts still to finalize during schematic work

- Two black 1×15, 2.54 mm female sockets: exact MPN, contact geometry, height, retention and current rating. JLCPCB stock/assembly not yet verified.
- Power rectifier diodes, input/output capacitors, current-setting resistor, decoupling and strap resistors.
- isoSPI matching network and any differential ESD components, with capacitance/pulse ratings calculated.
- Optional CAN common-mode choke, tuning resistors and test points.
- Indicator resistors and any transistor needed to respect GPIO drive limits.

Use 1206 passive footprints where requested, then specify actual capacitance under DC bias and temperature, resistor power/voltage limits, tolerance and package. No reference designators or final quantities are invented before schematic capture.

## Teensy 4.1 adapter (R0A)

JLCPCB stock observed through its parts-library search on **2026-11-08**. Quantities are per board. All passives are 1206.

| Function | Manufacturer / MPN | Qty | JLCPCB code | Observed stock |
|---|---|---:|---|---:|
| Controller (bought separately) | PJRC Teensy 4.1 with pins | 1 | — | — |
| Teensy sockets, 1 × 24, 8.5 mm | Hong Cheng HC-PM254-8.5H-1x24PZ | 2 | C41376163 | 19,453 |
| USB D+/D− pogo pins, 11 mm working height | YIYUAN YTC1P-8535-01 | 2 | C5221289 | 1,221 |
| USB-C receptacle | HRO TYPE-C-31-M-12 | 1 | C165948 | 317,944 |
| USB ESD | ST USBLC6-2SC6 | 1 | C7519 | 40,867 |
| VBUS fuse, 2 A hold | Littelfuse 1206L200PR | 1 | C151163 | 4,787 |
| VBUS TVS | Littelfuse SMAJ5.0A | 1 | C83329 | 38,636 |
| Schottky (Teensy VIN, rectifiers) | B5819W SL | 13 | C8598 | 854,425 |
| Isolated CAN transceiver | TI ISO1042DWR | 6 | C1848126 | 128 |
| CAN supply switch | TI TPS2553DBVR | 6 | C55266 | 57,740 |
| Push-pull driver | TI SN6505BDBVR | 6 | C74518 | 1,288 |
| Isolation transformer 1:1.3 | Würth 760390014 | 6 | C2802211 | 214 |
| Isolated 5 V LDO | TI TLV76750DGNR | 6 | C3752807 | 1,033 |
| CAN TVS | Nexperia PESD2CANFD24V-TR | 6 | C552486 | 18,015 |
| 120 Ω switch | E-Switch EG1218 | 6 | C273394 | 1,409 |
| DSUB-9 female, vertical | Connfly DS1034-09FBN044 | 6 | C19268322 | 572 |
| CAN FD controller | Microchip MCP2518FDT-E/SL | 3 | C626758 | 17,875 |
| 40 MHz crystal, 15 pF | YXC X322540MPB4SI | 3 | C9010 | 65,527 |
| Dual isoSPI bridge | ADI ADBMS6822WCCSZ-RL | 3 | C19190031 | 5,136 |
| isoSPI transformer | Bourns SM91801AL-E | 6 | C26423704 | **1** |
| isoSPI terminal | Phoenix Contact 1715721 | 6 | C480516 | 2,496 |
| LEDs | KENTO KT-1206G / KT-1206R | 8 / 1 | C14641 / C49018 | 15,717 / 33,207 |

**SM91801AL-E is the blocking item**: six are needed per board. JLCPCB offers pre-order for it. The well-stocked Bourns SM91502AL and Pulse HM2101NL / HM2103NL are specified with *functional* insulation, so they do not replace the basic-insulation part without a new insulation decision.

The complete list with values and designators is in the [engineering BOM](../manufacturing/prototype/T41-R0A/bom-engineering.csv).
