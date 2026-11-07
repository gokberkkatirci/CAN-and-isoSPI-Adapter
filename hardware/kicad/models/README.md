# 3D models

All **41 fitted carrier footprints** have a resolvable model in the KiCad 10 installation used to check R0A. Four NPTH mounting holes are modeled by the board geometry. The Nano module is drawn above J1/J2 using an additional model on J1.

| References | Model in the portable project | Exact CAD source or basis |
|---|---|---|
| C1–C14, R1–R10 | KiCad 1206 package models | KiCad 10 standard 3D library |
| D1–D3, U2–U5 | KiCad SOT-23, SMA, SOIC and MSOP package models | KiCad 10 standard 3D library |
| J1/J2, J3–J5 | KiCad female socket and Phoenix MKDS terminal models | KiCad 10 standard 3D library |
| U1 | Drawing-based LFCSP with 32 terminals and 2.10 mm exposed pad | [ADI package drawing 05-08-7057](https://www.analog.com/media/en/technical-documentation/data-sheets/adbms6821-adbms6822.pdf), Figure 43 |
| T1/T2 | Drawing-based SM91801AL-E body and leads | [Bourns datasheet](https://www.bourns.com/docs/product-datasheets/sm91801al.pdf), [vendor design files](https://www.bourns.com/resources/design-tools/engineering-files-list?folder=SM91801AL) |
| T3 | Drawing-based WE-PPTI body and leads | [Würth 760390014 resources](https://www.we-online.com/en/components/icref/texas-instruments/SN6501-TIDA-00794-Push-Pull), which list 250-1109 STEP |
| SW1 | Drawing-based EG1218 with a metal case, actuator and three tails | [E-Switch drawing](https://configured-product-images.s3.amazonaws.com/2D/specs/EG1218.pdf), [manufacturer STEP](https://configured-product-images.s3.amazonaws.com/stp3dmodels/EG1218.stp) |
| Nano R4 | Module envelope with USB-C shell, headers and representative components | [Arduino ABX00142 STEP archive](https://docs.arduino.cc/resources/models/ABX00142-step.zip), bare board variant |

The portable models load without a vendor account or downloads. Regenerate the original VRML files with [make_visual_models.py](../tools/make_visual_models.py). Their purpose is visual review and approximate packaging. Check socket engagement, enclosure clearances and actual vendor geometry before making mechanical tooling.

The Arduino and E-Switch STEP files were retrieved for local use. The Würth download returned HTTP 403 and the Bourns download could not be retrieved during this pass. Files from suppliers belong under the ignored `vendor/` directory so the public repository can be cloned without redistributing their CAD. Exact models may be substituted through the footprint's **3D Models** tab.

For a local vendor-model view, the downloaded Nano board can be added on J1 with an offset of **(−1.27, 3.81, 9.8) mm** and Z rotation of **90°**. The stock ABX00142 STEP omits the plug-in headers. The EG1218 STEP aligns at SW1 with a **+0.4 mm Z offset**. Both were checked together in a KiCad render. The original portable preview remains the default.
