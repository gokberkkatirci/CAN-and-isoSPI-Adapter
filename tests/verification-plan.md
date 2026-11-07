# Verification and acceptance plan

R0A schematic ERC, PCB DRC and schematic parity passed in KiCad 10.0.6. Hardware and firmware tests are pending. See [R0A notes](../docs/r0a.md).

## Before CAD release

1. Check every symbol pin and footprint pad against exact manufacturer drawings. Independently inspect Nano row orientation, transformer polarity, terminal numbering, switch throws and exposed pads.
2. Calculate USB power/inrush, unpowered-pin behavior, isolated supply flux/headroom, TVS clamping and termination dissipation across selected voltage/temperature ranges.
3. Establish the insulation-coordination specification for 1,000 V DC isoSPI operation. Record applicable environment, transients, PCB CTI and protective-insulation category. Inspect all layers and mechanical paths.
4. Obtain complete slave interface documentation and calculate timing margins for actual chain length/cables at 1 Mbit/s (1818) and target 2 Mbit/s (6832).
5. Pass ERC/DRC or record reviewed, justified exclusions; inspect Gerbers independently of the PCB editor. Check physical assembly and cable access in 3D and with the real module.

## Prototype bring-up

| Test | Conditions and evidence | Proposed acceptance |
|---|---|---|
| Unpowered inspection | Continuity, shorts, polarity, termination switch | 120 Ω within tolerance with switch ON; OFF disconnects that branch |
| USB and power | Supported source/cable voltage range, startup, load steps, suspend, reconnect | All rails within component operating limits; no reset/inrush violation |
| CAN interface | 125/250/500 kbit/s and 1 Mbit/s, standard/extended frames, realistic termination and cable | Correct transfer; no unexplained errors under declared test conditions |
| CAN startup/faults | Reset, watchdog, USB loss, power sequencing, bus-off | No unintended sustained dominant state; documented recovery |
| isoSPI MAIN/AUX | Each slave family separately, each port, target cable/chain sizes | No unexplained PEC/communication failures in recorded duration |
| Reversible operation | Connect ends of a supported chain; introduce controlled open link | Correct alternate-end access according to slave capability |
| Simultaneous acquisition | CAN worst declared frame load plus maximum isoSPI workload and host stalls | Zero unexplained losses; explicit overflow count for loads beyond supported envelope |
| Signal integrity | Differential waveforms at representative cable lengths and load extremes | Datasheet pulse/timing margins maintained |
| Temperature | Maximum declared ambient/load, enclosure closed if applicable | Junction/component margins maintained; no excessive terminal/termination heating |
| Protection/EMC | Defined ESD/transient levels using appropriate equipment | Behavior meets the subsequently frozen product specification |
| Isolation | Qualified test setup, defined voltage waveform/time/leakage limits | Meets the reviewed system-level procedure; component hipot values alone are not the test plan |

Do initial communication work with a low-energy battery-monitor simulator or equivalent controlled setup. High-voltage qualification requires a suitable guarded test arrangement. Keep grounded instruments from bridging intended isolation boundaries.

For logging, choose and record a duration (initial recommendation: at least one hour at the declared maximum workload) and compare sent/received counters. Exercise long host pauses: 32 KB total MCU SRAM does not establish an unlimited lossless buffer. Measure timestamp jitter and USB throughput; do not infer them from bus clock rates.

## Result records

For each tested revision record PCB revision, component variants, module/core/firmware versions, instruments, test scripts, cable/chain topology, voltage, temperature, duration, raw counters and pass/fail rationale. Store publishable results by revision; keep sensitive local data outside the committed result set. Numerical pass limits must be frozen before qualification rather than chosen after results are seen.
