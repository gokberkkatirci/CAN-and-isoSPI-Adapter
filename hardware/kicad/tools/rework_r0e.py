"""R0E transformer swap, applied once to the R0D board (run with KiCad's Python):

    python rework_r0e.py ../CAN_isoSPI_adapter.kicad_pcb

JLCPCB no longer stocks the R0D transformers, so R0E replaces them with stocked parts:

1. T3: Wurth 760390014 -> Maxinmicro MXPP6-3K6110. Same pinout and land pattern,
   swapped in place.
2. T1/T2: Bourns SM91801AL-E -> CND-tek HM1238NLTP (1000 V DC working, basic
   insulation). The new pad columns are 9.65 mm apart instead of 12.7 mm, so each
   transformer moves 1.825 mm to the right (x = 118.975 mm): the cable pads land on
   the existing tracks to J4/J5 and the chip-side pads sit 0.4 mm clear of the
   CS_MAIN via.
3. CS_MAIN, USB_5V and one AUX_IP run went straight down F.Cu between the old pad
   columns. They move to B.Cu (free there) so the new chip-side stubs do not cross
   them. All of them stay more than 9 mm from the cable-side pads.
4. Every route that ended under an old pad is joined to the matching new pad with one
   short F.Cu segment (one per group of touching route ends).
5. U5: TI TLV76750DGNR (56 left at JLCPCB) -> TPS7A1650QDGNRQ1 (2,505), same
   HVSSOP-8 land pattern and copper (see ldo()).
6. Title block revision becomes R0E; zones are refilled.
"""
import math
import sys

import pcbnew

PCB = sys.argv[1]
LIB = __file__.replace("\\", "/").rsplit("/tools/", 1)[0] + "/Carrier.pretty"
REV, DATE = "R0E", "2026-11-24"
b = pcbnew.LoadBoard(PCB)
MM = 1e6

PARTS = {
    "MXPP6": ("MXPP6-3K6110", "MXPP6-3K6110", "C19943838"),
    "HM1238": ("HM1238NLTP", "HM1238NLTP-CND", "C49230397"),
}


def pad_ends(fp):
    """{pad number: [(x, y) track endpoints of the pad's net inside the pad]} in IU."""
    out = {}
    for pad in fp.Pads():
        if not pad.GetNetname() or pad.GetNetname().startswith("unconnected"):
            continue
        box = pad.GetBoundingBox()
        pts, links = [], []
        for t in b.GetTracks():
            if t.GetClass() != "PCB_TRACK" or t.GetNetCode() != pad.GetNetCode() or t.GetLayer() != pcbnew.F_Cu:
                continue
            ends = [(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]
            inside = [e for e in ends if box.Contains(pcbnew.VECTOR2I(*e))]
            pts += inside
            if len(inside) == 2:
                links.append(tuple(inside))
        # group route ends that are joined by a segment lying under the pad
        groups = []
        for p in dict.fromkeys(pts):
            g = next((g for g in groups if any((p, q) in links or (q, p) in links for q in g)), None)
            if g is None:
                groups.append([p])
            else:
                g.append(p)
        out[pad.GetNumber()] = groups
    return out


def swap(ref, part, ends, pos=None, paths=None):
    val, mpn, lcsc = PARTS[part]
    old = b.FindFootprintByReference(ref)
    new = pcbnew.FootprintLoad(LIB, val)
    new.SetFPID(pcbnew.LIB_ID("Carrier", val))
    new.SetReference(ref)
    new.SetValue(val)
    new.SetPosition(pos if pos is not None else old.GetPosition())
    new.SetOrientationDegrees(old.GetOrientationDegrees())
    # keep reference/value text placement relative to the footprint
    for fo, fn in ((old.Reference(), new.Reference()), (old.Value(), new.Value())):
        fn.SetLayer(fo.GetLayer())
        fn.SetVisible(fo.IsVisible())
        fn.SetTextSize(fo.GetTextSize())
        fn.SetTextThickness(fo.GetTextThickness())
        fn.SetPosition(new.GetPosition() + (fo.GetPosition() - old.GetPosition()))
    for fname, ftext in (("MPN", mpn), ("JLCPCB Part #", lcsc)):
        layer = old.GetField(fname).GetLayer()
        new.SetField(fname, ftext)
        fld = new.GetField(fname)
        fld.SetVisible(False)
        fld.SetLayer(layer)
    new.SetPath(old.GetPath())
    new.SetSheetname(old.GetSheetname())
    new.SetSheetfile(old.GetSheetfile())
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/models/%s.wrl" % val
    new.Models().push_back(m)
    for pad in new.Pads():
        pad.SetNet(old.FindPadByNumber(pad.GetNumber()).GetNet())
    b.Add(new)
    b.Remove(old)
    if pos is None:
        return new
    for num, groups in ends.items():
        pad = new.FindPadByNumber(num)
        c = pad.GetPosition()
        if paths and num in paths:
            pts = [P(*q) for q in paths[num]] + [c]
            for s0, s1 in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(s0)
                t.SetEnd(s1)
                t.SetWidth(pcbnew.FromMM(0.2))
                t.SetLayer(pcbnew.F_Cu)
                t.SetNet(pad.GetNet())
                b.Add(t)
            continue
        for g in groups:
            e = min(g, key=lambda p: math.hypot(p[0] - c.x, p[1] - c.y))
            if pad.HitTest(pcbnew.VECTOR2I(*e)) and math.hypot(e[0] - c.x, e[1] - c.y) < 1:
                continue
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(*e))
            t.SetEnd(c)
            t.SetWidth(pcbnew.FromMM(0.2))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(pad.GetNet())
            b.Add(t)
    return new


LDO_PINS = {"2": "NC", "3": "PG", "6": "NC", "7": "DELAY"}


def ldo(ref):
    """TLV76750DGNR -> TPS7A1650QDGNRQ1 on the same land pattern and copper.

    On the fixed 5 V TPS7A16 pin 2 (FB/NC) and pin 6 have no internal connection, so
    pin 2 may stay on OUT and pin 6 on GND; PG (3) and DELAY (7) stay open."""
    fp = b.FindFootprintByReference(ref)
    fp.SetValue("TPS7A1650QDGNRQ1")
    fp.SetField("MPN", "TPS7A1650QDGNRQ1")
    fp.SetField("JLCPCB Part #", "C2832237")
    for pad in fp.Pads():
        if pad.GetNumber() in LDO_PINS:
            pad.SetPinFunction(LDO_PINS[pad.GetNumber()])
            pad.SetPinType("passive")
    for num, fn in (("3", "PG"), ("7", "DELAY")):   # keep the open pins' net names in step
        net = pcbnew.NETINFO_ITEM(b, "unconnected-(%s-%s-Pad%s)" % (ref, fn, num))
        b.Add(net)
        fp.FindPadByNumber(num).SetNet(net)


def P(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def seg(a, c, net, layer):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(P(*a))
    t.SetEnd(P(*c))
    t.SetWidth(pcbnew.FromMM(0.2))
    t.SetLayer(layer)
    t.SetNet(b.FindNet(net))
    b.Add(t)


def via(x, y, net):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(P(x, y))
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetNet(b.FindNet(net))
    b.Add(v)


def take(*segs):
    """Delete the F.Cu segments given as (net, a, c), in one pass over the board."""
    want = {(n, frozenset((a, c))) for n, a, c in segs}
    dead = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK" or t.GetLayer() != pcbnew.F_Cu:
            continue
        ends = frozenset(((round(pcbnew.ToMM(t.GetStart().x), 2), round(pcbnew.ToMM(t.GetStart().y), 2)),
                          (round(pcbnew.ToMM(t.GetEnd().x), 2), round(pcbnew.ToMM(t.GetEnd().y), 2))))
        if (t.GetNetname(), ends) in want:
            dead.append(t)
    if len(dead) != len(want):
        raise SystemExit("expected %d segments, found %d" % (len(want), len(dead)))
    for t in dead:
        b.Delete(t)


# Read the old pad/route geometry and delete copper before adding anything; KiCad 10's
# bindings cannot list board tracks again once items have been removed and added.
ENDS = {ref: pad_ends(b.FindFootprintByReference(ref)) for ref in ("T1", "T2")}

# ---- chip-side routes that ran on F.Cu between the old pad columns move to B.Cu,
# so the stubs to the new chip-side pads do not cross them.
take(("/CS_MAIN", (112.8, 72.3), (112.8, 103.3)),
     ("/USB_5V", (112.3, 75.8), (112.3, 88.8)),
     ("/AUX_IP", (112.2, 99.4), (112.2, 105.6)),
     ("/AUX_IP", (112.2, 105.6), (112.5, 105.9)),
     ("/AUX_IP", (112.5, 105.9), (112.5, 108.3)))
via(112.8, 72.3, "/CS_MAIN")              # the via at (112.8, 103.3) already exists
for a, c in (((112.8, 72.3), (113.3, 72.8)), ((113.3, 72.8), (113.3, 102.8)), ((113.3, 102.8), (112.8, 103.3))):
    seg(a, c, "/CS_MAIN", pcbnew.B_Cu)
via(112.3, 75.8, "/USB_5V")
via(112.3, 86.0, "/USB_5V")
seg((112.3, 75.8), (112.3, 86.0), "/USB_5V", pcbnew.B_Cu)
seg((112.3, 86.0), (112.3, 88.8), "/USB_5V", pcbnew.F_Cu)
via(112.2, 99.4, "/AUX_IP")
via(112.5, 108.0, "/AUX_IP")              # below the In2 INTR_MAIN/CS_MAIN diagonals
seg((112.2, 99.4), (112.2, 107.7), "/AUX_IP", pcbnew.B_Cu)
seg((112.2, 107.7), (112.5, 108.0), "/AUX_IP", pcbnew.B_Cu)
seg((112.5, 108.0), (112.5, 108.3), "/AUX_IP", pcbnew.F_Cu)

swap("T3", "MXPP6", {})
for ref, y in (("T1", 82.0), ("T2", 100.0)):
    # T2 pin 3: pass above the CS_MAIN via at (112.8, 103.3)
    paths = {"3": [(110.8, 102.5), (113.6, 102.5)]} if ref == "T2" else None
    swap(ref, "HM1238", ENDS[ref], P(118.975, y), paths)

ldo("U5")

tb = b.GetTitleBlock()
tb.SetRevision(REV)
tb.SetDate(DATE)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print("R0E rework applied to", PCB)
