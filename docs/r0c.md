# R0C notes (Nano R4 adapter)

R0C keeps the R0B placement, outline and routing. Two changes were made after a design review on 2026-11-08:

- **SN6505B CLK (U4 pin 6) is tied to USB ground.** The pin has an internal pull-down and the part falls back to its internal oscillator, but an open input next to the push-pull switch nodes can pick up noise. A short F.Cu stub and via connect it to the In1 ground plane.
- **R10 (82 kΩ current-limit resistor) uses UNI-ROYAL 1206W4F8202T5E (JLCPCB C17979).** The previous part had 14 units in stock.

The review also rechecked the isolated CAN supply against the SN6505B datasheet: Würth 760390014 is a 1:1.3 transformer intended for 5 V → 5 V with an LDO, so the TLV76750 keeps regulation headroom at the low end of USB voltage. Copper between USB ground and isolated CAN ground is at least 4 mm on every layer.

KiCad 10.0.6 reports zero ERC findings and zero DRC, unconnected-item and schematic-parity findings ([reports](../tests/R0C/)). The [test-point map](r0b.md#probe-points) is unchanged.
