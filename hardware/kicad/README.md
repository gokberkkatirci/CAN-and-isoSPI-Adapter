# KiCad design

Open [GK_CAN_isoSPI_adapter.kicad_pro](GK_CAN_isoSPI_adapter.kicad_pro) in **KiCad 10.0.6**. R0B uses a single schematic sheet with four circuit sections, a routed 82 × 64 mm PCB, and project-local symbols, footprints and 3D visualization models.

R0B adds six diagnostic probe pads. See the [test point map](../../docs/r0b.md).

Keep the schematic, PCB, project, custom rules and library tables together. The R0B PCB uses F.Cu for components and short signals, In1.Cu for separate USB and CAN ground zones, In2.Cu for the USB supply zone and routing, and B.Cu for routing. The cable domains are floating and the custom DRC rules preserve their copper separation.

In PCB Editor, choose **View → 3D Viewer**. See [model coverage](models/README.md) for the standard KiCad models, drawing-based models and optional manufacturer STEP files.
