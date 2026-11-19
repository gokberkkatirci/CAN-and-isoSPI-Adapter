"""R0B layout rework, applied once to the routed R0A board (run with KiCad's Python):

    python rework_r0b.py ../CAN6_isoSPI6_T41.kicad_pcb

The coordinates match the committed R0A route. A board re-routed by generate_t41.py
already has U1 in its R0B position and no TP4/TP7/TP8, but needs the VBUS path
(step 3) re-checked by hand.

1. Remove TP4 (VBUS), TP7 (USB_DP), TP8 (USB_DM) and every stub routed to them.
2. Move U1 (USBLC6) onto the D+/D- line beside the pogo pins, flow-through.
3. Rebuild VBUS J1 -> F1 as a 1.0 mm B.Cu track with 4 vias at J1 and 3 at F1.
4. Update silkscreen texts (revision, VIN-VUSB note, removed TP labels).
"""
import math
import sys
import pcbnew

PCB = sys.argv[1]
b = pcbnew.LoadBoard(PCB)
MM = 1e6
def P(x, y): return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))
def xy(v): return (v.x / MM, v.y / MM)
net = {n: b.FindNet(n) for n in ("/VBUS", "/USB_DP", "/USB_DM", "/GND")}

# ---- 1. test points ---------------------------------------------------------
for ref in ("TP4", "TP7", "TP8"):
    b.Delete(b.FindFootprintByReference(ref))

# ---- 2/3. delete old copper ---------------------------------------------------
def keep_usb(t):
    """Keep only the short F.Cu path J1 -> pogo pins (no vias, no stubs)."""
    if t.GetClass() == 'PCB_VIA' or t.GetLayer() != pcbnew.F_Cu:
        return False
    (x1, y1), (x2, y2) = xy(t.GetStart()), xy(t.GetEnd())
    if math.hypot(x2 - x1, y2 - y1) < 0.05:
        return False
    n = t.GetNetname()
    if n == "/USB_DM":
        return min(x1, x2) >= 38.2 and 81.6 <= min(y1, y2) and max(y1, y2) <= 83.4 and max(x1, x2) <= 44.8
    if n == "/USB_DP":
        return min(x1, x2) >= 37.1 and 82.6 <= min(y1, y2) and max(y1, y2) <= 84.4 and max(x1, x2) <= 44.8
    return False

dead = []
for t in b.GetTracks():
    n = t.GetNetname()
    if n == "/VBUS":
        dead.append(t)
    elif n in ("/USB_DP", "/USB_DM") and not keep_usb(t):
        dead.append(t)
    elif n == "/GND":
        # old U1 ground stub and via at (36.65, 73.00)
        if t.GetClass() == 'PCB_VIA':
            if abs(xy(t.GetPosition())[0] - 36.65) < 0.02 and abs(xy(t.GetPosition())[1] - 73.0) < 0.02:
                dead.append(t)
        else:
            ends = {tuple(round(c, 2) for c in xy(t.GetStart())), tuple(round(c, 2) for c in xy(t.GetEnd()))}
            if ends == {(37.86, 73.0), (36.65, 73.0)}:
                dead.append(t)
for t in dead:
    b.Delete(t)
print("removed", len(dead), "track/via items")

# ---- 2. move U1 ---------------------------------------------------------------
u1 = b.FindFootprintByReference("U1")
u1.SetPosition(P(48.5, 83.0))
u1.SetOrientationDegrees(180)
pad = {p.GetNumber(): xy(p.GetPosition()) for p in u1.Pads()}
print("U1 pads", {k: tuple(round(c, 2) for c in v) for k, v in sorted(pad.items())})
assert pad["4"][1] < pad["6"][1] and pad["4"][0] < pad["3"][0], "unexpected U1 pin orientation"

def trk(a, c, w, layer, n):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(int(w * MM)); t.SetLayer(layer); t.SetNet(net[n])
    b.Add(t)

def via(x, y, n, d=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(P(x, y)); v.SetWidth(int(d * MM)); v.SetDrill(int(drill * MM)); v.SetNet(net[n])
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    b.Add(v)

j4 = xy(b.FindFootprintByReference("J4").Pads()[0].GetPosition())   # D-
j5 = xy(b.FindFootprintByReference("J5").Pads()[0].GetPosition())   # D+
F = pcbnew.F_Cu
B = pcbnew.B_Cu
trk(j4, pad["4"], 0.2, F, "/USB_DM")
trk(pad["4"], pad["3"], 0.2, F, "/USB_DM")
trk(j5, pad["6"], 0.2, F, "/USB_DP")
trk(pad["6"], pad["1"], 0.2, F, "/USB_DP")
gv = (pad["2"][0] + 1.36, pad["2"][1])
trk(pad["2"], gv, 0.3, F, "/GND"); via(*gv, "/GND")
vv = (pad["5"][0] - 1.16, pad["5"][1])
trk(pad["5"], vv, 0.25, F, "/VBUS"); via(*vv, "/VBUS")

# ---- 3. VBUS: J1 pads -> vias -> 1.0 mm B.Cu -> vias -> F1.1 ----------------------
X = 40.4
trk((38.24, 80.55), (41.2, 80.55), 0.5, F, "/VBUS")          # A4/B9
trk((38.24, 85.45), (39.6, 85.45), 0.5, F, "/VBUS")          # A9/B4
trk((39.6, 85.45), (X, 85.95), 0.5, F, "/VBUS")
for x, y in ((X, 80.55), (41.2, 80.55), (40.8, 79.75), (X, 85.95)):
    via(x, y, "/VBUS")
trk((40.8, 79.75), (X, 80.55), 0.5, F, "/VBUS")
trk((X, 80.55), (41.2, 80.55), 1.0, B, "/VBUS")
trk((40.8, 79.75), (X, 80.55), 0.6, B, "/VBUS")
f1 = xy([p for p in b.FindFootprintByReference("F1").Pads() if p.GetNumber() == "1"][0].GetPosition())
YB = 100.0
trk((X, 80.55), (X, YB - 0.4), 1.0, B, "/VBUS")
trk((X, YB - 0.4), (f1[0], YB), 1.0, B, "/VBUS")
trk((39.7, YB), (41.3, YB), 1.0, B, "/VBUS")
for x in (39.7, f1[0], 41.3):
    via(x, YB, "/VBUS")
trk(f1, (f1[0], YB), 1.0, F, "/VBUS")
trk((39.7, YB), (41.3, YB), 0.8, F, "/VBUS")
trk(vv, (X, vv[1]), 0.3, B, "/VBUS")                         # USBLC6 VBUS reference

# ---- 4. silkscreen ------------------------------------------------------------------
for d in list(b.GetDrawings()):
    if d.GetClass() != 'PCB_TEXT':
        continue
    t = d.GetText(); x, y = xy(d.GetPosition())
    if t.startswith("CAN6_isoSPI6_T41 R0A"):
        d.SetText("CAN6_isoSPI6_T41 R0B  2026-11-19")
    elif t == "CUT VIN-VUSB ON TEENSY":
        d.SetText("KEEP VIN-VUSB JOINED")
    elif (t, round(x), round(y)) in (("VBUS", 134, 76), ("D+", 130, 80), ("D-", 134, 80)):
        b.Delete(d)
tb = b.GetTitleBlock(); tb.SetRevision("R0B"); tb.SetDate("2026-11-19")

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.Save(PCB)
print("saved")
