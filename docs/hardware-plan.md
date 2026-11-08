# Hardware plan — P0

Design baseline, 2026-11-07. The [R0A electrical notes](r0a.md) describe the circuit implemented in the [R0B layout](r0b.md). Source identifiers refer to [references](references.md). Values labelled provisional are engineering proposals, not verified production specifications.

## Requirements and selection

Use a socketed Arduino Nano R4 with headers (ABX00143), one Classical CAN interface up to 1 Mbit/s, and two isoSPI ports through an ADBMS6822. Two ports allow access to either end of a reversible chain or two independent chains; a single shared SPI bus services them sequentially. The [USB bridge firmware](../firmware/README.md) exposes raw isoSPI transfers for the host application. Native USB carries commands and acquired data and supports programming.

The requirement is 1 kV **working voltage**. For this battery application, the design interpretation is **1,000 V DC continuous across each isoSPI transformer barrier**. Select **two Bourns SM91801AL-E**. Basic insulation is the component baseline; whether the complete application needs reinforced insulation remains a system-level decision. The CAN barrier is a separate specification and is not assigned a 1 kV working rating by this selection.

The R0A carrier is 85 × 70 mm, with four layers and mostly 1206 resistors/capacitors. Physical module and enclosure fit are pending. CAN and isoSPI screw terminals occupy opposite edges. The Nano socket is the only defined module interface; no additional board-to-board mating connector is defined.

## Controller and USB

The Nano R4 provides native CAN and SPI, 5 V GPIO and USB-C in a small removable module. Its 32 KB SRAM is the main capture-buffer constraint [1–3]. Prefer it for this design because the Nano format and its onboard USB-C suit a compact adapter. A Teensy 4.1 sister board with six CAN and six isoSPI ports is documented separately in [hardware/teensy41](../hardware/teensy41/README.md); it uses a different socket, pin assignment and 3.3 V logic. A Linux-based Pi Zero adds a different power/software architecture without a demonstrated requirement here.

Use two black 1×15 female sockets. The module's USB-C connector faces the carrier's front edge and remains the only USB receptacle. The standard headers do not provide USB D+/D−. A second carrier-mounted USB port would require a different interconnect and is not part of this baseline. Retain physical reset/boot access and mechanical support for cable insertion forces.

Proposed signal allocation (logical Arduino names; physical socket pad numbering must be checked against the exact drawing):

| Nano pin | Carrier function | Status |
|---|---|---|
| D4 | CAN TX to ISO1042 TXD | Fixed native CAN function |
| D5 | CAN RX from ISO1042 RXD | Fixed native CAN function |
| D13 / D11 / D12 | SPI SCK / COPI / CIPO | Fixed SPI functions |
| D10 / D9 | MAIN / AUX chip select | Proposed; pull inactive high |
| D2 / D3 | MAIN / AUX INTR | Proposed inputs |
| D6 / D7 | MAIN / AUX WAKE status | Proposed inputs; do not drive in normal controller mode |
| D8 | Carrier load enable | Proposed; hardware default off |
| A3 | Current-limit fault input | Proposed; verify pull-up and polarity |
| D0 / D1 | Debug serial reserve | Keep available |
| 5V / GND | Carrier power / logic ground | USB-powered baseline |
| VIN / 3V3 / AREF | Unused by carrier baseline | Do not connect VIN to USB 5 V |

CAN/SPI assignments are checked against Arduino's documentation [1,2]. Other assignments are proposed. Check RA4M1 interrupt mappings and the exact Arduino core version before freezing the design.

## CAN circuit

The Nano supplies the CAN protocol controller; **ISO1042DWR** supplies the isolated physical interface [8]. No MCP2515 is needed. Use 5 V logic-side supply and a separately generated, regulated 5 V bus-side supply. All cable-side protection and the CAN reference terminal connect to isolated CAN ground, never USB ground.

Signal order: screw terminal → TVS/protection region → short differential route → transceiver. Candidate TVS is **Nexperia PESD2CANFD24V-TR**. Verify pulse clamping, capacitance and ground inductance against the complete fault specification. Optional common-mode-choke footprint may be reserved with bypass links; populate only after an EMI/signal-integrity assessment. ISO1042's bus-fault rating alone does not establish the assembled board's fault rating.

Switchable termination: **two 240 Ω, 1%, 1206 resistors in parallel** produce 120 Ω. An **E-Switch EG1218** mechanical switch connects/disconnects this branch across CAN H/L. Use its unused throw as open circuit; show OFF/120Ω clearly. With 0.25 W resistors the combined nominal rating is 0.5 W before derating. At 5 V differential, total dissipation is 5²/120 = 0.208 W; each resistor dissipates 0.104 W. This is normal-operation sizing, not protection against a continuous 24 V differential fault. Check the switch's exact drawing, contact rating and derating before release.

Provide a TXD pull-up for recessive startup. ISO1042 has no standby control in this proposed connection; listen-only behavior is a CAN-controller/firmware function. Verify reset, unpowered, brownout and cable-powered fault behavior experimentally.

## isoSPI circuit

**ADBMS6822WCCSZ-RL** provides two channels and supports bidirectional links up to 2 Mbit/s. Its MCU interface supports 5 V, so supply VDDS from the Nano logic rail. Set MSTR for controller operation; use standard bidirectional mode and SPI mode 0 as the initial strap configuration, following ADI's tables and evaluation guide [4,5]. Use separate chip selects with shared clock/data; only one channel is selected at a time. Add individual series-resistor footprints for signal-integrity tuning and separate status test points.

Use 5 V for VDD and VP in this USB-powered application. Fit local bypass capacitors at each supply pin, including at least the specified 1 µF at VDD. Do not assume key-off monitoring continues after USB removal. Review supply sequencing and status-pin levels before connecting them directly to the Nano [4].

Each channel gets its own **SM91801AL-E** transformer and two-pin terminal. Copy no generic Ethernet magnetics pinout: validate winding polarity, center taps, footprint and any unused pins from the exact manufacturer drawing. Start termination/matching design from ADI's circuit, then calculate against the actual cable and slave-board network. CAN's 120 Ω value is not automatically applicable to isoSPI. Final matching and any low-capacitance differential protection remain schematic-design tasks. No protection component may bridge a cable domain to USB ground.

**ADBMS1818 is a 1 Mbit/s device; ADBMS6832 advertises 2 Mbit/s isoSPI** [6,7]. Do not operate an 1818 chain at 2 Mbit/s or presume these ICs are interchangeable. The public 6832 document is a short datasheet: obtain its full timing/design information and exact slave-board revision before final compatibility sign-off. The common adapter topology is reasonable; detailed timing and magnetics compatibility still need verification. Active interrogation is supported; passive sniffing of a chain driven by another master is a different topology.

## 1 kV DC insulation implementation

SM91801AL-E is selected for its explicitly specified 1,000 V DC working voltage and basic insulation. Its separate dielectric test ratings are 4,300 V DC / 2,500 V AC. The datasheet specifies minimum 5 mm component creepage/clearance with stated environmental/material conditions [9]. These component dimensions do not define the required PCB spacing automatically.

Reserve an initial **8 mm board isolation corridor** around the isolated port domains, subject to the later insulation-coordination calculation and the transformer land pattern. This is a layout allowance, not a certified minimum. Calculate final spacing from actual PCB material CTI, pollution degree, altitude, transients, coating assumptions and protective-insulation requirement. Review all copper layers, pads, slots, screws, enclosure surfaces and external cable/terminal access. Keep MAIN and AUX domains appropriately separated from each other as well as from USB and CAN domains; they may be connected to different locations in a battery system.

No ground plane, test pad, silkscreen annotation implying safe touch, shield connection or mounting hardware may bypass a required barrier. Slots may increase creepage but do not automatically satisfy clearance. Neither a passing bench hipot test nor a transformer rating alone certifies the complete adapter for 1 kV operation.

The previously considered **Pulse HM2101NLT** has a stated 1 kV working voltage but functional insulation [10]. It is not an approved substitute for the selected basic-insulation Bourns part.

## Power design and budget

USB → Nano power path → 5 V header → **TPS2553DBVR** current-limited switch → external high-current loads. Keep load enable low until firmware has established its permitted USB power state. Logic supplies and signal states must be coordinated to prevent back-powering: provision VDDS from the MCU rail, gate VDD/VP and isolated CAN power only if ADI's sequencing requirements allow it. Final rail partition is a schematic review item.

Candidate isolated CAN supply: **SN6505BDBVR + Würth 760390014 + rectifiers + TLV76750DGNR**. The power transformer and regulator require worst-case headroom, magnetic flux, rectifier loss and thermal calculations [11–13]. The 760390014 datasheet specifies an AC insulation test; a 1 kV DC continuous working rating for this complete supply has not been established. The proposed CAN isolation is intended for a low-voltage CAN network and must be redesigned if the CAN side also needs a 1 kV working barrier.

Provisional budgeting allowances, not measured current:

| Load | USB-side allocation |
|---|---:|
| Nano and its onboard circuitry | 100 mA |
| Dual isoSPI bridge and local logic | 40 mA |
| Isolated CAN supply | 180 mA |
| Indicators and miscellaneous | 10 mA |
| Design margin | 70 mA |
| **Planning target** | **400 mA** |

Do not treat a USB-C connector as permission to draw arbitrary current. Validate enumeration/suspend behavior, inrush, current-limit tolerances and module/header losses against the actual USB source. Check minimum header voltage against both interface supply limits. Verify regulated CAN 5 V during dominant transmission, startup, no-load and USB voltage droop. No external power is exported through the signal terminals.

## Layout and manufacturing intent

Use L1 components/signals, L2 local ground planes, L3 local power/ground and L4 remaining signals. Maintain the isolation gaps through every layer. Route high-edge-rate signals over their own uninterrupted reference plane; keep SPI short and away from the push-pull power loop. Use 45° bends or arcs and rounded board corners. Avoid long terminal stubs, thin return necks and routing beneath the isolation barrier.

Initial low-voltage rules: 0.20 mm track/clearance, 0.30 mm finished via hole with 0.60 mm pad, and 0.50 mm copper-to-outline allowance; these are proposed design margins, not JLCPCB limits. Fine-pitch fanout needs local verified rules. Use the actual quoted four-layer stackup, nominal 1.6 mm thickness and appropriate FR-4 material. Set isolation rules separately from ordinary clearance.

Use 1206 for carrier resistors and most capacitors; select voltage rating, DC-bias derating, tolerance and temperature grade per net. ICs, diodes, magnetics, sockets and connectors retain their required packages. This requirement does not change parts already fitted to the Nano. Keep decoupling loop area small even with 1206 capacitors.

Use **Phoenix Contact 1715734** for CAN H/L/isolated GND and **two separate 1715721** terminals for MAIN/AUX pairs. Their durable through-hole bodies suit repeated lab use. Their published connector ratings must be reviewed in the actual enclosure/barrier arrangement; no claim of a 1 kV-rated exposed terminal assembly is made. Terminal contact-to-contact voltage and terminal-to-user/domain insulation are different checks [15].

The JLCPCB path is mixed SMT/THT assembly, with the Nano installed separately unless procurement explicitly supports it. Exact sockets, remaining power diodes, passives and protection parts must be finalized before generating a production BOM. Refer to [components](components.md), [release conditions](decisions.md), and [verification](../tests/verification-plan.md).
