# 3D models

Nano R4 adapter: all **41 fitted carrier footprints** have a resolvable model in the KiCad 10 installation used to check R0B to R0E. The mounting holes and six exposed test pads are represented by PCB geometry. The Nano module is drawn above J1/J2 using an additional model on J1.

| References | Model in the portable project | Exact CAD source or basis |
|---|---|---|
| C1–C14, R1–R10 | KiCad 1206 package models | KiCad 10 standard 3D library |
| D1–D3, U2–U5 | KiCad SOT-23, SMA, SOIC and MSOP package models | KiCad 10 standard 3D library |
| J1/J2, J3–J5 | KiCad female socket and Phoenix MKDS terminal models | KiCad 10 standard 3D library |
| U1 | Drawing-based LFCSP with 32 terminals and 2.10 mm exposed pad | [ADI package drawing 05-08-7057](https://www.analog.com/media/en/technical-documentation/data-sheets/adbms6821-adbms6822.pdf), Figure 43 |
| T1/T2 | `HM1238NLTP.wrl`: drawing-based body and gull-wing leads (7.69 × 8.1 mm body, 4.25 mm tall, 10.5 mm over the leads, 3.81/2.54 mm lead pitch) | CND-tek HM1238NLTP datasheet drawing ([JLCPCB C49230397](https://jlcpcb.com/partdetail/C49230397)) |
| T3 | `MXPP6-3K6110.wrl`: drawing-based body and leads (7.10 × 6.55 mm, 4.2 mm tall, 2.54 mm pitch) | Maxinmicro MXPP6-3K6110 datasheet ([JLCPCB C19943838](https://jlcpcb.com/partdetail/C19943838)) |
| SW1 | Drawing-based EG1218 with a metal case, actuator and three tails | [E-Switch drawing](https://configured-product-images.s3.amazonaws.com/2D/specs/EG1218.pdf), [manufacturer STEP](https://configured-product-images.s3.amazonaws.com/stp3dmodels/EG1218.stp) |
| Nano R4 | Module envelope with USB-C shell, headers and representative components | [Arduino ABX00142 STEP archive](https://docs.arduino.cc/resources/models/ABX00142-step.zip), bare board variant |

The portable models load without a vendor account or downloads. Regenerate the original VRML files with [make_visual_models.py](../tools/make_visual_models.py). Their purpose is visual review and approximate packaging. Check socket engagement, enclosure clearances and actual vendor geometry before making mechanical tooling.

The Arduino and E-Switch STEP files were retrieved for local use. The Würth download returned HTTP 403 and the Bourns download could not be retrieved during this pass. Files from suppliers belong under the ignored `vendor/` directory so the public repository can be cloned without redistributing their CAD. Exact models may be substituted through the footprint's **3D Models** tab.

For a local vendor-model view, the downloaded Nano board can be added on J1 with an offset of **(−1.27, 3.81, 9.8) mm** and Z rotation of **90°**. The stock ABX00142 STEP omits the plug-in headers. The EG1218 STEP aligns at SW1 with a **+0.4 mm Z offset**. Both were checked together in a KiCad render. The original portable preview remains the default.

## Teensy 4.1 adapter

Every fitted footprint on the Teensy board has a model; only the test pads and mounting holes are left as PCB geometry. Standard parts (1206 passives, SOT-23, SOT-23-6, SOIC, MSOP, SMA, SOD-123, 1206 LEDs, 3225 crystal, PTC, DSUB-9, Phoenix terminals and 1 × 24 sockets) use the KiCad 10 library. These drawing-based VRML models were added for it:

| References | Model | Basis |
|---|---|---|
| U701, U801, U901 / T701–T902 / T101–T601 / SW101–SW601 | Same ADBMS6822, HM1238NLTP, MXPP6-3K6110 and EG1218 models as the Nano adapter | See above |
| J2 (second model) | `Teensy41-mounted.wrl`: Teensy 4.1 resting on 8.5 mm sockets, with micro-USB, processor, flash, microSD socket and header pins | PJRC Teensy 4.1 dimensions and pinout card |
| J4, J5 | `Pogo_YTC1P-8535.wrl`: 2 mm barrel, 12 mm free length | YIYUAN YTC1P-8535-01 listing |
| J1 | `USB_C_HRO_TYPE-C-31-M-12.wrl`: receptacle shell, opening and leads | HRO TYPE-C-31-M-12 drawing; KiCad 10 has no model for this footprint |

Regenerate all models with [make_visual_models.py](../tools/make_visual_models.py).
