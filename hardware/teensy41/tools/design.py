"""Single source of truth for the Teensy 4.1 six-CAN / six-isoSPI carrier.

Every part, pin-to-net connection, footprint, placement and purchasing code is
defined here. ``generate_t41.py`` turns this description into the KiCad
schematic, PCB and manufacturing files, so the schematic and the board cannot
drift apart.

Coordinates are millimetres from the top-left board corner. KiCad rotation is
counter-clockwise in degrees.
"""

PROJECT = "CAN6_isoSPI6_T41"
TITLE = "Six CAN and six isoSPI adapter - Teensy 4.1"
REV = "R0A"
DATE = "2026-11-08"

BOARD_W = 216.0
BOARD_H = 120.0
CORNER_R = 3.0

# --- Layout constants -------------------------------------------------------
CAN_CX = [25.5 + 33.0 * i for i in range(6)]        # DSUB column centres
PORT_X = list(CAN_CX)                                # isoSPI port N sits opposite CAN port N
ADBMS_X = [(PORT_X[2 * k] + PORT_X[2 * k + 1]) / 2.0 for k in range(3)]
ADBMS_Y = 36.5
ISO_T_Y = 20.0                                      # isoSPI transformer centre
TERM_Y = 5.65                                       # isoSPI terminal pin row
TEENSY_X1 = 14.0                                    # first header pin (USB end)
TEENSY_YC = 53.0
TEENSY_ROW_A_Y = TEENSY_YC + 7.62                   # GND, 0..12, 3V3, 24..32
TEENSY_ROW_B_Y = TEENSY_YC - 7.62                   # VIN, GND, 3V3, 23..13, GND, 41..33
BARRIER_Y0 = 83.5                                   # CAN isolation band
BARRIER_Y1 = 88.5
ISO_BAND_Y = 23.5                                   # isoSPI 8 mm band ends here
DSUB_ORIGIN_DY = BOARD_H - 10.94                    # rear pin row (pins 1-5)

STD = "std"     # KiCad standard footprint libraries
LOC = "T41"     # project-local library (T41Carrier.pretty)

# --- Purchasing data (JLCPCB parts library checked 2026-11-08) --------------
# name: (value, MPN, manufacturer, JLCPCB code, footprint lib, footprint, assembly)
PARTS = {
    "C100n":  ("100nF", "CL31B104KBCNNNC", "Samsung", "C24497", "Capacitor_SMD", "C_1206_3216Metric", "SMT"),
    "C1u":    ("1uF", "CL31B105KBHNNNE", "Samsung", "C1848", "Capacitor_SMD", "C_1206_3216Metric", "SMT"),
    "C10u":   ("10uF", "CL31A106KBHNNNE", "Samsung", "C13585", "Capacitor_SMD", "C_1206_3216Metric", "SMT"),
    "C22p":   ("22pF", "CC1206JKNPOCBN220", "YAGEO", "C107174", "Capacitor_SMD", "C_1206_3216Metric", "SMT"),
    "C4n7HV": ("4.7nF 2kV", "1206B472K202NT", "FH", "C41017", "Capacitor_SMD", "C_1206_3216Metric", "SMT"),
    "R100":   ("100R", "1206W4F1000T5E", "UNI-ROYAL", "C17901", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R240":   ("240R", "1206W4F2400T5E", "UNI-ROYAL", "C17961", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R1k":    ("1k", "1206W4F1001T5E", "UNI-ROYAL", "C4410", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R2k2":   ("2.2k", "1206W4F2201T5E", "UNI-ROYAL", "C17948", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R5k1":   ("5.1k", "1206W4F5101T5E", "UNI-ROYAL", "C26033", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R10k":   ("10k", "1206W4F1002T5E", "UNI-ROYAL", "C17902", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R100k":  ("100k", "1206W4F1003T5E", "UNI-ROYAL", "C17900", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R130k":  ("130k", "1206W4F1303T5E", "UNI-ROYAL", "C82092", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "R1M":    ("1M", "1206W4F1004T5E", "UNI-ROYAL", "C17927", "Resistor_SMD", "R_1206_3216Metric", "SMT"),
    "PTC2A":  ("2A PTC", "1206L200PR", "Littelfuse", "C151163", "Fuse", "Fuse_1206_3216Metric", "SMT"),
    "TVS5V":  ("SMAJ5.0A", "SMAJ5.0A", "Littelfuse", "C83329", "Diode_SMD", "D_SMA", "SMT"),
    "SCHOT":  ("B5819W", "B5819W SL", "Changjing", "C8598", "Diode_SMD", "D_SOD-123", "SMT"),
    "LEDG":   ("Green", "KT-1206G", "KENTO", "C14641", "LED_SMD", "LED_1206_3216Metric", "SMT"),
    "LEDR":   ("Red", "KT-1206R", "KENTO", "C49018", "LED_SMD", "LED_1206_3216Metric", "SMT"),
    "USBC":   ("USB-C", "TYPE-C-31-M-12", "HRO", "C165948", "Connector_USB", "USB_C_Receptacle_HRO_TYPE-C-31-M-12", "SMT"),
    "USBESD": ("USBLC6-2SC6", "USBLC6-2SC6", "STMicroelectronics", "C7519", "Package_TO_SOT_SMD", "SOT-23-6", "SMT"),
    "ISO1042": ("ISO1042DWR", "ISO1042DWR", "Texas Instruments", "C1848126", "Package_SO", "SOIC-16W_7.5x10.3mm_P1.27mm", "SMT"),
    "TPS2553": ("TPS2553DBVR", "TPS2553DBVR", "Texas Instruments", "C55266", "Package_TO_SOT_SMD", "SOT-23-6", "SMT"),
    "SN6505": ("SN6505BDBVR", "SN6505BDBVR", "Texas Instruments", "C74518", "Package_TO_SOT_SMD", "SOT-23-6", "SMT"),
    "WE760":  ("760390014", "760390014", "Wurth Elektronik", "C2802211", LOC, "WE_760390014", "SMT"),
    "TLV767": ("TLV76750DGNR", "TLV76750DGNR", "Texas Instruments", "C3752807", "Package_SO", "MSOP-8-1EP_3x3mm_P0.65mm_EP1.73x1.85mm", "SMT"),
    "PESD":   ("PESD2CANFD24V-TR", "PESD2CANFD24V-TR", "Nexperia", "C552486", "Package_TO_SOT_SMD", "SOT-23", "SMT"),
    "EG1218": ("EG1218", "EG1218", "E-Switch", "C273394", LOC, "EG1218", "THT"),
    "DSUB9F": ("DSUB-9 female", "DS1037-09FNAKT74-0CC", "CONNFLY", "C75749", "Connector_Dsub",
               "DSUB-9_Socket_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm", "THT"),
    "MCP2518": ("MCP2518FDT-E/SL", "MCP2518FDT-E/SL", "Microchip", "C626758", "Package_SO", "SOIC-14_3.9x8.7mm_P1.27mm", "SMT"),
    "XTAL40": ("40MHz", "X322540MPB4SI", "YXC", "C9010", "Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm", "SMT"),
    "ADBMS":  ("ADBMS6822WCCSZ-RL", "ADBMS6822WCCSZ-RL", "Analog Devices", "C19190031", LOC, "ADBMS6822_05-08-7057", "SMT"),
    "SM918":  ("SM91801AL-E", "SM91801AL-E", "Bourns", "C26423704", LOC, "SM91801AL-E", "SMT"),
    "MKDS2":  ("isoSPI terminal", "1715721", "Phoenix Contact", "C480516", "TerminalBlock_Phoenix",
               "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", "THT"),
    "SOCK24": ("Teensy socket 1x24", "HC-PM254-8.5H-1x24PZ", "Hong Cheng", "C41376163", "Connector_PinSocket_2.54mm",
               "PinSocket_1x24_P2.54mm_Vertical", "THT"),
    "POGO":   ("Pogo pin", "YTC1P-8535-01", "YIYUAN", "C5221289", LOC, "Pogo_YTC1P-8535_D2.0mm", "SMT"),
    "TP":     ("Test pad", "", "", "", "TestPoint", "TestPoint_Pad_D1.5mm", "NONE"),
    "HOLE":   ("M3 mounting hole", "", "", "", "MountingHole", "MountingHole_3.2mm_M3", "NONE"),
}

# --- Symbols ----------------------------------------------------------------
# kind "box": left/right pin lists of (number, name, electrical type); None is a gap.
# kind "two": two-pin part using one of the graphic styles from the R0B library.
P, PI, PO, IN, OUT, BI, OC = "passive", "power_in", "power_out", "input", "output", "bidirectional", "open_collector"

SYMBOLS = {
    "resistor": dict(kind="two", style="resistor", ref="R", names=("~", "~")),
    "capacitor": dict(kind="two", style="capacitor", ref="C", names=("~", "~")),
    "fuse": dict(kind="two", style="resistor", ref="F", names=("~", "~")),
    "diode": dict(kind="two", style="diode", ref="D", names=("K", "A")),
    "tvs": dict(kind="two", style="diode", ref="D", names=("K", "A")),
    "led": dict(kind="two", style="diode", ref="D", names=("K", "A")),
    "testpoint": dict(kind="tp", ref="TP"),
    "hole": dict(kind="hole", ref="H"),
    "flag": dict(kind="flag", ref="#FLG"),
    "pogo": dict(kind="box", ref="J", w=10.16, left=[("1", "PAD", P)], right=[]),
    "USB_C": dict(kind="box", ref="J", w=15.24,
                  left=[("A4", "VBUS", P), ("A9", "VBUS", P), ("B4", "VBUS", P), ("B9", "VBUS", P), None,
                        ("A5", "CC1", P), ("B5", "CC2", P), None, ("A8", "SBU1", P), ("B8", "SBU2", P)],
                  right=[("A6", "D+", P), ("B6", "D+", P), ("A7", "D-", P), ("B7", "D-", P), None,
                         ("A1", "GND", P), ("A12", "GND", P), ("B1", "GND", P), ("B12", "GND", P), ("SH", "SHIELD", P)]),
    "USBLC6": dict(kind="box", ref="U", w=15.24,
                   left=[("1", "IO1", P), ("6", "IO1", P), ("5", "VBUS", P)],
                   right=[("3", "IO2", P), ("4", "IO2", P), ("2", "GND", P)]),
    "T41_ROW_A": dict(kind="box", ref="J", w=15.24,
                      left=[("%d" % (i + 1), n, t) for i, (n, t) in enumerate(
                          [("GND", P)] + [("D%d" % k, BI) for k in range(0, 13)] + [("3V3", PO)] +
                          [("D%d" % k, BI) for k in range(24, 33)])], right=[]),
    "T41_ROW_B": dict(kind="box", ref="J", w=15.24,
                      left=[("%d" % (i + 1), n, t) for i, (n, t) in enumerate(
                          [("VIN", P), ("GND", P), ("3V3", P)] + [("D%d" % k, BI) for k in range(23, 12, -1)] +
                          [("GND", P)] + [("D%d" % k, BI) for k in range(41, 32, -1)])], right=[]),
    "ISO1042": dict(kind="box", ref="U", w=30.48,
                    left=[("1", "VCC1", PI), ("2", "GND1", PI), ("3", "TXD", IN), ("4", "NC", P), ("5", "RXD", OUT),
                          ("6", "NC", P), ("7", "NC", P), ("8", "GND1", PI)],
                    right=[("16", "VCC2", PI), ("15", "GND2", PI), ("14", "NC", P), ("13", "CANH", BI), ("12", "CANL", BI),
                           ("11", "VCC2", PI), ("10", "GND2", PI), ("9", "GND2", PI)]),
    "TPS2553": dict(kind="box", ref="U", w=20.32,
                    left=[("1", "IN", PI), ("2", "GND", PI), ("3", "EN", IN)],
                    right=[("6", "OUT", PO), ("5", "ILIM", P), ("4", "FAULT", OC)]),
    "SN6505B": dict(kind="box", ref="U", w=20.32,
                    left=[("2", "VCC", PI), ("5", "EN", IN), ("6", "CLK", IN)],
                    right=[("1", "D1", OC), ("3", "D2", OC), ("4", "GND", PI)]),
    "WE760390014": dict(kind="box", ref="T", w=20.32,
                        left=[("1", "PRI1", P), ("2", "PRI_CT", P), ("3", "PRI2", P)],
                        right=[("6", "SEC1", P), ("5", "SEC_CT", P), ("4", "SEC2", P)]),
    "TLV76750": dict(kind="box", ref="U", w=20.32,
                     left=[("8", "IN", PI), ("5", "EN", IN), ("3", "NC", P), ("7", "NC", P)],
                     right=[("1", "OUT", PO), ("2", "SNS", IN), ("4", "GND", PI), ("6", "GND", PI), ("9", "EP", PI)]),
    "PESD2CANFD": dict(kind="box", ref="D", w=15.24,
                       left=[("1", "IO1", P), ("2", "IO2", P)], right=[("3", "COMMON", P)]),
    "EG1218": dict(kind="switch", ref="SW"),
    "DSUB9F": dict(kind="box", ref="J", w=15.24,
                   left=[("1", "NC1", P), ("2", "CAN_L", P), ("3", "CAN_GND", P), ("4", "NC4", P), ("5", "SHLD", P)],
                   right=[("6", "CAN_GND", P), ("7", "CAN_H", P), ("8", "NC8", P), ("9", "NC9", P), ("SH", "SHELL", P)]),
    "MCP2518FD": dict(kind="box", ref="U", w=25.4,
                      left=[("14", "VDD", PI), ("13", "nCS", IN), ("10", "SCK", IN), ("11", "SDI", IN), ("12", "SDO", "tri_state"),
                            ("4", "nINT", OUT), ("9", "INT0", BI), ("8", "INT1", BI), ("7", "VSS", PI)],
                      right=[("1", "TXCAN", OUT), ("2", "RXCAN", IN), ("3", "CLKO", OUT), ("6", "OSC1", IN), ("5", "OSC2", OUT)]),
    "XTAL4": dict(kind="box", ref="Y", w=10.16, left=[("1", "X1", P), ("2", "GND", P)], right=[("3", "X2", P), ("4", "GND", P)]),
    "ADBMS6822": dict(kind="box", ref="U", w=30.48,
                      left=[("1", "MSTR", P), ("2", "PICO", P), ("3", "POCI", P), ("4", "SCK", P), ("5", "CS", P),
                            ("6", "VDDS", PI), ("7", "INTR", P), ("8", "WAKE", P), ("9", "GND", PI), ("10", "IM", P),
                            ("11", "IP", P), ("12", "VDD", PI), ("13", "VP", PI), ("14", "PHAPOL", P), ("15", "RTO", P),
                            ("16", "XCVRMD", P), ("33", "EP", PI)],
                      right=[("25", "MSTR2", P), ("26", "PICO2", P), ("27", "POCI2", P), ("28", "SCK2", P), ("29", "CS2", P),
                             ("30", "VDDS2", PI), ("31", "INTR2", P), ("32", "WAKE2", P), ("17", "GND2", PI), ("18", "IM2", P),
                             ("19", "IP2", P), ("20", "VDD2", PI), ("21", "VP2", PI), ("22", "PHAPOL2", P), ("23", "RTO2", P),
                             ("24", "XCVRMD2", P)]),
    "SM91801AL": dict(kind="box", ref="T", w=25.4,
                      left=[("1", "PRI+", P), ("2", "PRI_CT", P), ("3", "PRI-", P)],
                      right=[("6", "SEC+", P), ("5", "SEC_CT", P), ("4", "SEC-", P)]),
    "TERM2": dict(kind="box", ref="J", w=10.16, left=[("2", "+", P), ("1", "-", P)], right=[]),
}

# --- Netlist ------------------------------------------------------------------
parts = []          # list of dicts, see add()
flags = []          # nets that receive an ERC power flag
NC = None           # marker for no-connect pins


def add(ref, sym, kind, pins, pos, group, value=None, dnp=False):
    """pins: {pin_number: net_name or NC}. pos: (x, y, rot) on the PCB or None."""
    parts.append(dict(ref=ref, sym=sym, part=kind, pins=pins, pos=pos, group=group, value=value, dnp=dnp))


def R(ref, kind, a, b, pos, group):
    add(ref, "resistor", kind, {"1": a, "2": b}, pos, group)


def C(ref, kind, a, b, pos, group):
    add(ref, "capacitor", kind, {"1": a, "2": b}, pos, group)


# ---- USB-C, power entry and controller ----
G = "Power and USB"
add("J1", "USB_C", "USBC", {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "USB_CC1", "B5": "USB_CC2",
                            "A8": NC, "B8": NC, "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DM", "B7": "USB_DM",
                            "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "SH": "USB_SHIELD"},
    (4.2, TEENSY_YC, 270), G)
add("U1", "USBLC6", "USBESD", {"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM", "5": "VBUS", "2": "GND"},
    (9.0, 43.0, 0), G)
R("R1", "R5k1", "USB_CC1", "GND", (18.5, 49.0, 0), G)
R("R2", "R5k1", "USB_CC2", "GND", (18.5, 56.0, 0), G)
R("R3", "R1k", "USB_CC1", "CC1_SENSE", (23.5, 49.0, 0), G)
R("R4", "R1k", "USB_CC2", "CC2_SENSE", (23.5, 56.0, 0), G)
add("F1", "fuse", "PTC2A", {"1": "VBUS", "2": "+5V"}, (10.5, 67.0, 90), G)
add("D1", "tvs", "TVS5V", {"1": "+5V", "2": "GND"}, (15.5, 68.0, 90), G)
C("C1", "C10u", "+5V", "GND", (29.0, 49.0, 0), G)
C("C2", "C100n", "+5V", "GND", (34.0, 49.0, 0), G)
R("R5", "R1M", "USB_SHIELD", "GND", (3.5, 63.5, 90), G)
C("C3", "C4n7HV", "USB_SHIELD", "GND", (7.0, 63.5, 90), G)
add("D2", "diode", "SCHOT", {"1": "T_VIN", "2": "+5V"}, (15.0, 41.0, 0), G)
R("R6", "R2k2", "+5V", "LED_5V_A", (4.0, 71.0, 90), G)
add("D3", "led", "LEDG", {"1": "GND", "2": "LED_5V_A"}, (4.0, 76.0, 90), G)
C("C4", "C10u", "+3V3", "GND", (40.0, 56.5, 0), G)
C("C5", "C100n", "+3V3", "GND", (45.0, 56.5, 0), G)
R("R9", "R10k", "CAN_PWR_FAULT", "+3V3", (55.0, 56.5, 0), G)
R("R7", "R1k", "LED_OK", "LED_OK_A", (80.0, 50.0, 0), G)
add("D4", "led", "LEDG", {"1": "GND", "2": "LED_OK_A"}, (85.0, 50.0, 180), G)
R("R8", "R1k", "LED_ERR", "LED_ERR_A", (80.0, 54.0, 0), G)
add("D5", "led", "LEDR", {"1": "GND", "2": "LED_ERR_A"}, (85.0, 54.0, 180), G)
for i, (net, x) in enumerate([("+5V", 92.0), ("GND", 96.0), ("+3V3", 100.0), ("CAN_PWR_FAULT", 92.0),
                              ("T_SPARE32", 96.0)]):
    y = 50.0 if i < 3 else 55.0
    add("TP%d" % (i + 1), "testpoint", "TP", {"1": net}, (x, y, 0), G)
for i, (x, y) in enumerate([(4.5, 4.5), (211.5, 4.5), (4.5, 115.5), (211.5, 115.5), (108.0, 4.5), (108.0, 56.0)]):
    add("H%d" % (i + 1), "hole", "HOLE", {}, (x, y, 0), G)

G = "Teensy 4.1"
row_a = ["GND", "CAN2_RX", "CAN2_TX", "ISO_INT1", "ISO_INT2", "ISO_INT3", "ISO_CS6", "ISO_CS5", "ISO_CS4", "ISO_CS3",
         "ISO_CS2", "ISO_CS1", "ISO_MOSI", "ISO_MISO", "+3V3", "CAN6_EN", "CAN_PWR_FAULT", "MCP_MOSI", "MCP_SCK",
         "LED_OK", "LED_ERR", "CAN3_RX", "CAN3_TX", "T_SPARE32"]
row_b = ["T_VIN", "GND", "+3V3", "CAN1_RX", "CAN1_TX", "CAN5_EN", "CAN4_EN", "CAN3_EN", "CAN2_EN", "CAN1_EN",
         "ISO_INT6", "ISO_INT5", "ISO_INT4", "ISO_SCK", "GND", "CC2_SENSE", "CC1_SENSE", "MCP_MISO", "MCP_CS4",
         "MCP_CS5", "MCP_CS6", "MCP_INT4", "MCP_INT5", "MCP_INT6"]
add("J2", "T41_ROW_A", "SOCK24", {str(i + 1): n for i, n in enumerate(row_a)}, (TEENSY_X1, TEENSY_ROW_A_Y, 90), G,
    value="Teensy 4.1 row GND-0-32")
add("J3", "T41_ROW_B", "SOCK24", {str(i + 1): n for i, n in enumerate(row_b)}, (TEENSY_X1, TEENSY_ROW_B_Y, 90), G,
    value="Teensy 4.1 row VIN-23-33")
# Teensy 4.1 USB device pads on the module underside: 0.73 mm inboard of the
# end pin column; D+ is on the GND/0 row side, D- on the VIN side.
add("J4", "pogo", "POGO", {"1": "USB_DM"}, (TEENSY_X1 + 0.73, TEENSY_YC - 1.27, 0), G, value="Pogo USB D-")
add("J5", "pogo", "POGO", {"1": "USB_DP"}, (TEENSY_X1 + 0.73, TEENSY_YC + 1.27, 0), G, value="Pogo USB D+")

# ---- Six isolated CAN channels ----
for n in range(1, 7):
    b = 100 * n
    cx = CAN_CX[n - 1]
    G = "CAN%d" % n
    I = lambda s: "CAN%dI_%s" % (n, s)  # noqa: E731 - isolated-domain net names
    add("U%d" % (b + 1), "ISO1042", "ISO1042",
        {"1": "+3V3", "2": "GND", "3": "CAN%d_TX" % n, "4": NC, "5": "CAN%d_RX" % n, "6": NC, "7": NC, "8": "GND",
         "9": I("GND"), "10": I("GND"), "11": I("5V"), "12": I("L"), "13": I("H"), "14": NC, "15": I("GND"),
         "16": I("5V")}, (cx - 6.0, 86.0, 270), G)
    add("U%d" % (b + 2), "TPS2553", "TPS2553",
        {"1": "+5V", "2": "GND", "3": "CAN%d_EN" % n, "4": "CAN_PWR_FAULT", "5": "CAN%d_ILIM" % n,
         "6": "CAN%d_PWR" % n}, (cx + 2.5, 75.0, 0), G)
    add("U%d" % (b + 3), "SN6505B", "SN6505",
        {"1": "CAN%d_PPA" % n, "2": "CAN%d_PWR" % n, "3": "CAN%d_PPB" % n, "4": "GND", "5": "CAN%d_PWR" % n,
         "6": "GND"}, (cx + 9.0, 77.5, 90), G)
    add("T%d" % (b + 1), "WE760390014", "WE760",
        {"1": "CAN%d_PPB" % n, "2": "CAN%d_PWR" % n, "3": "CAN%d_PPA" % n, "4": I("RB"), "5": I("GND"),
         "6": I("RA")}, (cx + 9.0, 86.0, 270), G)
    add("D%d" % (b + 1), "diode", "SCHOT", {"1": I("RECT"), "2": I("RA")}, (cx + 14.0, 95.0, 90), G)
    add("D%d" % (b + 2), "diode", "SCHOT", {"1": I("RECT"), "2": I("RB")}, (cx + 4.0, 95.0, 90), G)
    add("U%d" % (b + 4), "TLV76750", "TLV767",
        {"1": I("5V"), "2": I("5V"), "3": NC, "4": I("GND"), "5": I("RECT"), "6": I("GND"), "7": NC,
         "8": I("RECT"), "9": I("GND")}, (cx + 9.0, 99.5, 0), G)
    add("D%d" % (b + 3), "PESD2CANFD", "PESD", {"1": I("H"), "2": I("L"), "3": I("GND")}, (cx - 4.5, 96.0, 0), G)
    add("SW%d" % (b + 1), "EG1218", "EG1218", {"1": I("TERM"), "2": I("H"), "3": NC}, (cx - 6.0, 103.8, 0), G,
        value="120R termination")
    R("R%d" % (b + 1), "R240", I("TERM"), I("L"), (cx - 10.5, 97.5, 90), G)
    R("R%d" % (b + 2), "R240", I("TERM"), I("L"), (cx - 13.5, 97.5, 90), G)
    add("J%d" % (b + 1), "DSUB9F", "DSUB9F",
        {"1": NC, "2": I("L"), "3": I("GND"), "4": NC, "5": I("SHLD"), "6": I("GND"), "7": I("H"), "8": NC,
         "9": NC, "SH": I("SHLD")}, (cx + 5.54, DSUB_ORIGIN_DY, 0), G, value="CAN%d DSUB-9F" % n)
    R("R%d" % (b + 3), "R1M", I("SHLD"), I("GND"), (cx + 6.0, 104.2, 0), G)
    C("C%d" % (b + 1), "C4n7HV", I("SHLD"), I("GND"), (cx + 11.0, 104.2, 0), G)
    R("R%d" % (b + 4), "R130k", "CAN%d_ILIM" % n, "GND", (cx + 2.5, 71.0, 0), G)
    R("R%d" % (b + 5), "R100k", "CAN%d_EN" % n, "GND", (cx - 3.5, 70.0, 90), G)
    R("R%d" % (b + 6), "R10k", "CAN%d_TX" % n, "+3V3", (cx - 6.0, 77.5, 0), G)
    R("R%d" % (b + 7), "R2k2", I("5V"), I("LED"), (cx + 14.0, 100.0, 90), G)
    add("D%d" % (b + 4), "led", "LEDG", {"1": I("GND"), "2": I("LED")}, (cx - 14.0, 103.5, 90), G)
    C("C%d" % (b + 2), "C100n", "+5V", "GND", (cx - 1.0, 75.0, 90), G)
    C("C%d" % (b + 3), "C10u", "CAN%d_PWR" % n, "GND", (cx + 13.9, 73.2, 90), G)
    C("C%d" % (b + 4), "C100n", "CAN%d_PWR" % n, "GND", (cx + 13.9, 78.0, 90), G)
    C("C%d" % (b + 5), "C10u", I("RECT"), "CAN%dI_GND" % n, (cx + 9.0, 94.0, 0), G)
    C("C%d" % (b + 6), "C10u", I("5V"), I("GND"), (cx + 4.0, 100.5, 90), G)
    C("C%d" % (b + 7), "C100n", I("5V"), I("GND"), (cx - 8.0, 94.5, 90), G)
    C("C%d" % (b + 8), "C100n", I("5V"), I("GND"), (cx - 1.0, 94.5, 90), G)
    C("C%d" % (b + 9), "C100n", "+3V3", "GND", (cx + 2.0, 78.6, 0), G)
    flags.extend([I("GND"), I("RECT")])
    if n >= 4:
        add("U%d" % (b + 5), "MCP2518FD", "MCP2518",
            {"1": "CAN%d_TX" % n, "2": "CAN%d_RX" % n, "3": NC, "4": "MCP_INT%d" % n, "5": "CAN%d_XO" % n,
             "6": "CAN%d_XI" % n, "7": "GND", "8": NC, "9": NC, "10": "MCP_SCK", "11": "MCP_MOSI",
             "12": "MCP_MISO", "13": "MCP_CS%d" % n, "14": "+3V3"}, (cx - 9.0, 68.5, 0), G)
        add("Y%d" % (b + 1), "XTAL4", "XTAL40",
            {"1": "CAN%d_XI" % n, "2": "GND", "3": "CAN%d_XO" % n, "4": "GND"}, (cx - 15.0, 69.5, 90), G)
        C("C%d" % (b + 10), "C22p", "CAN%d_XI" % n, "GND", (cx - 15.2, 74.2, 0), G)
        C("C%d" % (b + 11), "C22p", "CAN%d_XO" % n, "GND", (cx - 15.0, 65.0, 0), G)
        C("C%d" % (b + 12), "C100n", "+3V3", "GND", (cx - 9.0, 62.6, 0), G)
        R("R%d" % (b + 8), "R10k", "MCP_CS%d" % n, "+3V3", (cx - 2.0, 63.5, 0), G)
        R("R%d" % (b + 9), "R10k", "MCP_INT%d" % n, "+3V3", (cx + 3.0, 63.5, 0), G)

# ---- Three dual isoSPI bridges / six ports ----
for k in range(1, 4):
    b = 600 + 100 * k
    x = ADBMS_X[k - 1]
    G = "isoSPI %d-%d" % (2 * k - 1, 2 * k)
    pa, pb = 2 * k, 2 * k - 1       # channel 1 -> right port, channel 2 -> left port
    add("U%d" % (b + 1), "ADBMS6822", "ADBMS",
        {"1": "+3V3", "2": "ISO_MOSI", "3": "ISO_MISO", "4": "ISO_SCK", "5": "ISO_CS%d" % pa, "6": "+3V3",
         "7": "ISO_INT%d" % pa, "8": NC, "9": "GND", "10": "ISO%d_IM" % pa, "11": "ISO%d_IP" % pa, "12": "+5V",
         "13": "+5V", "14": "GND", "15": "GND", "16": "GND", "17": "GND", "18": "ISO%d_IM" % pb,
         "19": "ISO%d_IP" % pb, "20": "+5V", "21": "+5V", "22": "GND", "23": "GND", "24": "GND", "25": "+3V3",
         "26": "ISO_MOSI", "27": "ISO_MISO", "28": "ISO_SCK", "29": "ISO_CS%d" % pb, "30": "+3V3",
         "31": "ISO_INT%d" % pb, "32": NC, "33": "GND"}, (x, ADBMS_Y, 90), G)
    C("C%d" % (b + 1), "C100n", "+3V3", "GND", (x - 8.0, 33.0, 90), G)
    C("C%d" % (b + 2), "C100n", "+3V3", "GND", (x + 8.0, 33.0, 90), G)
    C("C%d" % (b + 3), "C1u", "+5V", "GND", (x - 8.0, 40.0, 90), G)
    C("C%d" % (b + 4), "C100n", "+5V", "GND", (x - 11.0, 40.0, 90), G)
    C("C%d" % (b + 5), "C1u", "+5V", "GND", (x + 8.0, 40.0, 90), G)
    C("C%d" % (b + 6), "C100n", "+5V", "GND", (x + 11.0, 40.0, 90), G)
    R("R%d" % (b + 1), "R10k", "ISO_CS%d" % pa, "+3V3", (x + 11.0, 33.0, 90), G)
    R("R%d" % (b + 2), "R10k", "ISO_CS%d" % pb, "+3V3", (x - 11.0, 33.0, 90), G)
    for j, p in enumerate((pb, pa)):
        xp = PORT_X[p - 1]
        add("T%d" % (b + 1 + j), "SM91801AL", "SM918",
            {"1": "ISO%d_IP" % p, "2": NC, "3": "ISO%d_IM" % p, "4": "ISO%dC_N" % p, "5": NC,
             "6": "ISO%dC_P" % p}, (xp, ISO_T_Y, 90), G)
        R("R%d" % (b + 3 + j), "R100", "ISO%d_IP" % p, "ISO%d_IM" % p, (xp, 30.0, 0), G)
        add("J%d" % (b + 1 + j), "TERM2", "MKDS2", {"1": "ISO%dC_N" % p, "2": "ISO%dC_P" % p},
            (xp + 2.54, TERM_Y, 180), G, value="isoSPI %d" % p)

flags.extend(["GND", "+5V", "VBUS"])

# Net classes: (track, clearance) in mm
NETCLASS_POWER = (0.3, 0.2)
NETCLASS_HIGHCURRENT = (0.8, 0.2)
HIGH_CURRENT_NETS = {"VBUS", "T_VIN"}
NETCLASS_SIGNAL = (0.25, 0.2)
POWER_NETS = {"+5V", "GND", "+3V3"}
for n in range(1, 7):
    POWER_NETS |= {"CAN%d_PWR" % n, "CAN%d_PPA" % n, "CAN%d_PPB" % n, "CAN%dI_5V" % n, "CAN%dI_GND" % n,
                   "CAN%dI_RECT" % n, "CAN%dI_RA" % n, "CAN%dI_RB" % n}


def can_domain(net):
    """Return channel number if net belongs to an isolated CAN domain."""
    if net and net.startswith("CAN") and len(net) > 4 and net[4] == "I" and net[3].isdigit():
        return int(net[3])
    return None
