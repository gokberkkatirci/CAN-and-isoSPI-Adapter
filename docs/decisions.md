# Decisions and unresolved release conditions

Updated 2026-11-07. The planning decisions below precede the [R0A prototype implementation](r0a.md).

## Recorded decisions

- isoSPI is the battery-monitor interface; slave families are ADBMS1818 and ADBMS6832.
- Native MCU USB is acceptable; firmware implementation belongs to the user.
- Arduino Nano R4 with headers (ABX00143) is the controller baseline.
- Two female sockets and the Nano's own edge-accessible USB-C port are proposed.
- The user's 1 kV requirement means working voltage. Battery-context interpretation: 1,000 V DC continuous across each isoSPI barrier.
- Select two Bourns SM91801AL-E transformers. Do not substitute a functional-insulation part without reviewing the system requirement.
- Four layers, <100 × 100 mm, predominantly 1206 passives, switchable CAN termination and opposite-edge screw terminals.
- Separate project directory with native KiCad source and a GitHub remote. R0B adds compact placement, diagnostic pads and Nano R4 bench firmware.

## Information and engineering work needed before schematic freeze

| Item | Why it matters | Current disposition |
|---|---|---|
| Existing main-board socket drawing/pinout | Mechanical and electrical mating | Not supplied; no mating compatibility claimed |
| Exact 6832 suffix/full documentation and both slave schematics | Timing, polarity, magnetics and matching | Public short datasheet is insufficient for full sign-off |
| Cable type, impedance, maximum length and chain size | Link margin and termination | Open |
| Basic vs reinforced insulation, altitude, pollution degree, CTI, transient environment | Board and enclosure insulation coordination | Bourns basic-insulation component selected; system requirement open |
| Maximum actual pack-to-USB voltage including tolerance | 1,000 V is a limit, not extra transient margin | Open |
| CAN-side isolation/fault environment | Isolated DC/DC selection and TVS coordination | Low-voltage CAN network assumed; no 1 kV CAN working claim |
| Exact Nano/socket mechanics and current path | USB access, power droop, retention | Verify physical module and official drawing |
| Sustained logging workload and tolerated loss/host stalls | 32 KB RAM may constrain acquisition | Validate with user's firmware |
| Production quantity and procurement | Two selected transformers required per board; observed stock one | JLCPCB replenishment/preorder/consignment needed |

## Before layout release

Complete schematic ERC, manufacturer pin-by-pin footprint review, power/thermal and insulation calculations, exact passive selection, approved assembly process and connector access review. All unresolved numeric ratings must be resolved or explicitly excluded from the released specification.

## Before fabrication order

Complete DRC, layer-by-layer barrier inspection, enclosure/metal clearance review and BOM/CPL visual cross-check. Recheck stock and reserve enough parts including assembly attrition. Generate fabrication files only from the reviewed PCB revision. Do not label the hardware as tested/certified before the corresponding evidence exists.
