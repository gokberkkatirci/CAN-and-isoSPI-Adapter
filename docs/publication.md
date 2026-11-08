# Publication notes

The repository contains editable KiCad source for both adapters, the generator script for the Teensy 4.1 board, original visual models, two Arduino-style sketches with build instructions, and clearly labeled prototype manufacturing exports. Source references and model provenance are recorded in [third-party materials](../THIRD_PARTY.md).

Before each public push, check tracked files and history for credentials, local workspace paths, local KiCad settings (`*.kicad_prl` is ignored) and downloaded supplier CAD (`hardware/kicad/models/vendor/` is ignored). Generated routing intermediates under `hardware/teensy41/build/` and compiled firmware are ignored as well.

No reuse license has been chosen yet. Until one is added, the default copyright rules apply. Typical choices are CERN-OHL-P or CERN-OHL-S for hardware and MIT or Apache-2.0 for firmware.
