"""R0C transformer swap, applied once to the routed R0B board (run with KiCad's Python):

    python rework_r0c.py ../CAN6_isoSPI6_T41.kicad_pcb

JLCPCB no longer stocks the R0B transformers, so R0C replaces them with stocked parts:

1. T101-T601: Wurth 760390014 -> Maxinmicro MXPP6-3K6110. Same pinout and land
   pattern (pads at +/-4.57 mm, 2.54 mm pitch), so the footprint is swapped in place
   and no copper moves.
2. T701-T902: Bourns SM91801AL-E -> CND-tek HM1238NLTP (1000 V DC working, basic
   insulation). The new land pattern is smaller (pad columns 9.65 mm apart instead of
   12.7 mm, uneven 3.81/2.54 mm row pitch), so each transformer moves to y = 19.6 mm
   (D.ISO_T_Y) where both pad rows clear the 16.5-23.5 mm isoSPI band and the cable
   pads keep 8 mm to the logic planes that start at 23.5 mm.
3. Cable-side tracks are rebuilt as generate_t41.py now draws them; on the chip side
   one short F.Cu stub joins each new pad to the end of the existing R0B route.
4. U104-U604: TI TLV76750DGNR (56 left at JLCPCB) -> TPS7A1650QDGNRQ1 (2,505), same
   HVSSOP-8 land pattern and copper (see ldo()).
5. Revision text and title block move to R0C; zones are refilled.
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design as D  # noqa: E402

PCB = sys.argv[1]
LIB = os.path.join(os.path.dirname(HERE), "T41Carrier.pretty")
OX, OY = 30.0, 30.0
b = pcbnew.LoadBoard(PCB)


def P(x, y):
    """Board-local millimetres (top-left board corner) to KiCad units."""
    return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY + y))


def track(a, c, w, net):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(P(*a))
    t.SetEnd(P(*c))
    t.SetWidth(pcbnew.FromMM(w))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    b.Add(t)


def swap(ref, part, pos=None):
    """Replace footprint `ref` with the library footprint of D.PARTS[part], keeping nets and links."""
    val, mpn, mfr, lcsc, lib, fpn, asm = D.PARTS[part]
    old = b.FindFootprintByReference(ref)
    new = pcbnew.FootprintLoad(LIB, fpn)
    if new is None:
        raise SystemExit("footprint not found: " + fpn)
    new.SetFPID(pcbnew.LIB_ID(lib, fpn))
    new.SetReference(ref)
    new.SetValue(val)
    for fname, ftext in (("MPN", mpn), ("JLCPCB Part #", lcsc)):
        new.SetField(fname, ftext)
        fld = new.GetField(fname)
        fld.SetVisible(False)
        fld.SetLayer(pcbnew.F_Fab)
    new.SetPath(old.GetPath())
    new.SetSheetname(old.GetSheetname())
    new.SetSheetfile(old.GetSheetfile())
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/../kicad/models/%s.wrl" % fpn
    new.Models().push_back(m)
    new.SetPosition(pos if pos is not None else old.GetPosition())
    new.SetOrientationDegrees(old.GetOrientationDegrees())
    for pad in new.Pads():
        pad.SetNet(old.FindPadByNumber(pad.GetNumber()).GetNet())
    b.Add(new)
    r = new.Reference()
    r.SetLayer(pcbnew.F_Fab)
    r.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
    r.SetTextThickness(pcbnew.FromMM(0.12))
    b.Remove(old)
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


# ---- 1. isolated CAN supply transformers ------------------------------------
for n in range(1, 7):
    swap("T%d" % (100 * n + 1), "MXPP6")

# ---- 2/3. isoSPI transformers and their copper --------------------------------
for k in range(1, 4):
    base = 600 + 100 * k
    for j, p in enumerate((2 * k - 1, 2 * k)):
        ref = "T%d" % (base + 1 + j)
        xp = D.PORT_X[p - 1]
        old = b.FindFootprintByReference(ref)
        # R0B pad centres, where the existing chip-side routes end
        old_ip = pcbnew.VECTOR2I(old.FindPadByNumber("1").GetPosition())
        old_im = pcbnew.VECTOR2I(old.FindPadByNumber("3").GetPosition())
        new = swap(ref, "HM1238", P(xp, D.ISO_T_Y))
        for num, old_pos in (("1", old_ip), ("3", old_im)):
            pad = new.FindPadByNumber(num)
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pad.GetPosition())
            t.SetEnd(old_pos)
            t.SetWidth(pcbnew.FromMM(0.2))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(pad.GetNet())
            b.Add(t)
        # cable side: drop the R0B straight tracks and draw the R0C ones
        for nn in ("/ISO%dC_P" % p, "/ISO%dC_N" % p):
            for t in [t for t in b.GetTracks() if t.GetNetname() == nn]:
                b.Remove(t)
        pad_y = D.ISO_T_Y - 4.825
        for sgn, nn in ((-1, "/ISO%dC_P" % p), (1, "/ISO%dC_N" % p)):
            net = b.FindNet(nn)
            track((xp + sgn * 3.175, pad_y), (xp + sgn * 2.54, pad_y - 0.635), 0.8, net)
            track((xp + sgn * 2.54, pad_y - 0.635), (xp + sgn * 2.54, D.TERM_Y), 0.8, net)

# ---- 4. isolated 5 V regulators ----------------------------------------------
for n in range(1, 7):
    ldo("U%d" % (100 * n + 4))

# ---- 5. revision, title block, zones ------------------------------------------
for d in b.GetDrawings():
    if d.GetClass() == "PCB_TEXT" and d.GetText().startswith(D.PROJECT + " R0"):
        d.SetText("%s %s  %s" % (D.PROJECT, D.REV, D.DATE))
tb = b.GetTitleBlock()
tb.SetRevision(D.REV)
tb.SetDate(D.DATE)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print("R0C rework applied to", PCB)
