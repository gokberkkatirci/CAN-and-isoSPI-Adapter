# KiCad design (Nano R4 adapter)

Open [CAN_isoSPI_adapter.kicad_pro](CAN_isoSPI_adapter.kicad_pro) in **KiCad 10.0.6** or newer. R0E uses a single schematic sheet with four circuit sections, a routed 82 × 64 mm PCB, and project-local symbols, footprints and 3D visualization models.

The board has six diagnostic probe pads. See the [test point map](../../docs/r0b.md#probe-points) and the [R0C](../../docs/r0c.md), [R0D](../../docs/r0d.md) and [R0E](../../docs/r0e.md) changes. Mount H3 with nylon hardware only.

Keep the schematic, PCB, project, custom rules and library tables together. The PCB uses F.Cu for components and short signals, In1.Cu for separate USB and CAN ground zones, In2.Cu for the USB supply zone and routing, and B.Cu for routing. The cable domains are floating and the custom DRC rules preserve their copper separation.

In PCB Editor, choose **View → 3D Viewer**. See [model coverage](models/README.md) for the standard KiCad models, drawing-based models and optional manufacturer STEP files. The Teensy 4.1 adapter in [../teensy41](../teensy41/README.md) reuses these models.
