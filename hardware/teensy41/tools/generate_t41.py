"""Generate the Teensy 4.1 carrier schematic, PCB and fabrication data.

Run with KiCad's bundled Python (it provides ``pcbnew``)::

    PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
    $PY hardware/teensy41/tools/generate_t41.py all

Stages: ``sch`` writes the symbol library, schematic, project and rules;
``pcb`` places footprints and zones; ``route`` runs Freerouting through a
Specctra round trip; ``finish`` fills zones and saves; ``fab`` writes the
JLCPCB BOM/CPL. ``all`` runs every stage in order. Freerouting is located via
the FREEROUTING_JAR and JAVA environment variables.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design as D  # noqa: E402

PRJ_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PRJ_DIR))
NAME = D.PROJECT
SCH = os.path.join(PRJ_DIR, NAME + ".kicad_sch")
PCB = os.path.join(PRJ_DIR, NAME + ".kicad_pcb")
PRO = os.path.join(PRJ_DIR, NAME + ".kicad_pro")
LIBSYM = os.path.join(PRJ_DIR, "T41Carrier.kicad_sym")
KICAD_FP = os.environ.get("KICAD_FOOTPRINT_DIR", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
OX, OY = 30.0, 30.0           # board origin on the KiCad page
NS = uuid.UUID("6b1f6c1e-4f0e-4b5b-9d4a-2a1d4a7c6e01")


def uid(*parts):
    return str(uuid.uuid5(NS, "/".join(str(p) for p in parts)))


ROOT_UUID = uid("root")


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


# =============================================================================
# Symbols
# =============================================================================
TWO_GRAPHICS = {
    "resistor": '(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))',
    "capacitor": '(polyline (pts (xy -0.65 -2.03) (xy -0.65 2.03)) (stroke (width 0.254) (type default)) (fill (type none)))'
                 '(polyline (pts (xy 0.65 -2.03) (xy 0.65 2.03)) (stroke (width 0.254) (type default)) (fill (type none)))',
    "diode": '(polyline (pts (xy -1.27 -1.7) (xy -1.27 1.7)) (stroke (width 0.254) (type default)) (fill (type none)))'
             '(polyline (pts (xy 1.27 -1.7) (xy 1.27 1.7) (xy -1.27 0) (xy 1.27 -1.7)) (stroke (width 0.254) (type default)) (fill (type none)))',
}
TWO_PINLEN = {"resistor": 2.54, "capacitor": 4.43, "diode": 3.81}


def pin_s(ptype, x, y, ang, length, name, num):
    return ('(pin %s line (at %s %s %d) (length %s) (name %s (effects (font (size 0.95 0.95)))) '
            '(number %s (effects (font (size 0.9 0.9)))))' % (ptype, fmt(x), fmt(y), ang, fmt(length), q(name), q(num)))


def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def box_geometry(sd):
    """Return (half_width, rows_top_y, pin list with lib coordinates)."""
    left, right = sd.get("left", []), sd.get("right", [])
    n = max(len(left), len(right), 1)
    top = math.ceil((n - 1) / 2.0) * 2.54
    hw = sd["w"] / 2.0
    pins = []
    for side, lst in (("L", left), ("R", right)):
        for i, p in enumerate(lst):
            if p is None:
                continue
            y = top - i * 2.54
            x = -(hw + 2.54) if side == "L" else hw + 2.54
            pins.append(dict(num=p[0], name=p[1], type=p[2], x=x, y=y, side=side))
    return hw, top, n, pins


def symbol_def(name, prefix=""):
    sd = D.SYMBOLS[name]
    full = prefix + name
    kind = sd["kind"]
    head = '(symbol %s ' % q(full)
    body = []
    if kind == "two":
        st = sd["style"]
        L = TWO_PINLEN[st]
        head += '(pin_numbers (hide yes)) (pin_names (hide yes)) (in_bom yes) (on_board yes)'
        body.append('(symbol "%s_0_1" %s)' % (name, TWO_GRAPHICS[st]))
        body.append('(symbol "%s_1_1" %s %s)' % (name, pin_s("passive", -5.08, 0, 0, L, sd["names"][0], "1"),
                                                pin_s("passive", 5.08, 0, 180, L, sd["names"][1], "2")))
    elif kind == "flag":
        head += '(pin_numbers (hide yes)) (pin_names (hide yes)) (in_bom no) (on_board no)'
        body.append('(symbol "flag_0_1" (polyline (pts (xy -1.27 2.54) (xy 0 3.81) (xy 1.27 2.54) (xy -1.27 2.54)) '
                    '(stroke (width 0.254) (type default)) (fill (type none))))')
        body.append('(symbol "flag_1_1" %s)' % pin_s("power_out", 0, 0, 90, 2.54, "~", "1"))
    elif kind == "tp":
        head += '(pin_names (offset 0.6)) (in_bom no) (on_board yes)'
        body.append('(symbol "testpoint_0_1" (circle (center 0 2.54) (radius 1.0) (stroke (width 0.254) (type default)) (fill (type none))))')
        body.append('(symbol "testpoint_1_1" %s)' % pin_s("passive", 0, 0, 90, 1.54, "~", "1"))
    elif kind == "hole":
        head += '(pin_names (offset 0.6)) (in_bom no) (on_board yes)'
        body.append('(symbol "hole_0_1" (circle (center 0 0) (radius 1.5) (stroke (width 0.254) (type default)) (fill (type none))))')
    elif kind == "switch":
        head += '(pin_numbers (hide yes)) (pin_names (hide yes)) (in_bom yes) (on_board yes)'
        body.append('(symbol "EG1218_0_1" (polyline (pts (xy -3.81 0) (xy 1.8 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))'
                    '(polyline (pts (xy 2.25 2.54) (xy 3.81 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))'
                    '(polyline (pts (xy 2.25 -2.54) (xy 3.81 -2.54)) (stroke (width 0.254) (type default)) (fill (type none))))')
        body.append('(symbol "EG1218_1_1" %s %s %s)' % (pin_s("passive", 6.35, 2.54, 180, 2.54, "ON", "1"),
                                                       pin_s("passive", -6.35, 0, 0, 2.54, "COM", "2"),
                                                       pin_s("passive", 6.35, -2.54, 180, 2.54, "OFF", "3")))
    else:
        hw, top, n, pins = box_geometry(sd)
        bottom = top - (n - 1) * 2.54
        head += '(pin_names (offset 0.6)) (in_bom yes) (on_board yes)'
        body.append('(symbol "%s_0_1" (rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) '
                    '(fill (type background))))' % (name, fmt(-hw), fmt(top + 2.54), fmt(hw), fmt(bottom - 2.54)))
        ps = [pin_s(p["type"], p["x"], p["y"], 0 if p["side"] == "L" else 180, 2.54, p["name"], p["num"]) for p in pins]
        body.append('(symbol "%s_1_1" %s)' % (name, " ".join(ps)))
    props = ('(property "Reference" %s (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))) '
             '(property "Value" %s (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))) '
             '(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))) '
             '(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))) '
             '(property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))') % (q(sd["ref"]), q(name))
    return head + "\n  " + props + "\n  " + "\n  ".join(body) + ")"


def symbol_pins(name):
    """Pin connection points in library coordinates."""
    sd = D.SYMBOLS[name]
    k = sd["kind"]
    if k == "two":
        return {"1": (-5.08, 0.0, "L"), "2": (5.08, 0.0, "R")}
    if k in ("flag", "tp"):
        return {"1": (0.0, 0.0, "D")}
    if k == "hole":
        return {}
    if k == "switch":
        return {"1": (6.35, 2.54, "R"), "2": (-6.35, 0.0, "L"), "3": (6.35, -2.54, "R")}
    _, _, _, pins = box_geometry(sd)
    return {p["num"]: (p["x"], p["y"], p["side"]) for p in pins}


def symbol_pin_names(name):
    sd = D.SYMBOLS[name]
    k = sd["kind"]
    if k == "two":
        return {"1": sd["names"][0], "2": sd["names"][1]}
    if k == "switch":
        return {"1": "ON", "2": "COM", "3": "OFF"}
    if k in ("tp", "flag"):
        return {"1": "~"}
    if k == "hole":
        return {}
    _, _, _, pins = box_geometry(sd)
    return {p["num"]: p["name"] for p in pins}


def symbol_extent(name):
    sd = D.SYMBOLS[name]
    k = sd["kind"]
    if k == "two":
        return 10.16, 5.08
    if k == "switch":
        return 12.7, 7.62
    if k in ("tp", "hole", "flag"):
        return 5.08, 7.62
    hw, top, n, _ = box_geometry(sd)
    return 2 * hw + 5.08, (n + 1) * 2.54


def write_symbol_lib():
    used = sorted({p["sym"] for p in D.parts} | {"flag"})
    with open(LIBSYM, "w") as f:
        f.write("(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)\n")
        for s in used:
            f.write(symbol_def(s) + "\n")
        f.write(")\n")
    return used


# =============================================================================
# Schematic
# =============================================================================
def unconnected_name(ref, pinname, num):
    if pinname in ("~", ""):
        return "unconnected-(%s-Pad%s)" % (ref, num)
    return "unconnected-(%s-%s-Pad%s)" % (ref, pinname, num)


def part_value(p):
    return p["value"] or D.PARTS[p["part"]][0]


def part_fp(p):
    _, _, _, _, lib, fp, _ = D.PARTS[p["part"]]
    return "%s:%s" % (lib if lib != D.STD else lib, fp)


def write_schematic(used):
    out = []
    out.append('(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0") (uuid %s) (paper "A0")' % ROOT_UUID)
    out.append('(title_block (title %s) (rev %s) (date %s) (comment 1 "Prototype / bench validation pending") '
               '(comment 2 "Generated by hardware/teensy41/tools/generate_t41.py"))' % (q(D.TITLE), q(D.REV), q(D.DATE)))
    out.append("(lib_symbols")
    for s in used:
        out.append(symbol_def(s, prefix="T41:"))
    out.append(")")

    groups = []
    for p in D.parts:
        if p["group"] not in groups:
            groups.append(p["group"])
    # Section layout: power/teensy on top row, six CAN sections, three isoSPI sections
    page_w = 1189.0
    sec_w = 290.0
    col_x = [20.0, 310.0, 600.0, 890.0]
    cursor = {}
    order = ["Power and USB", "Teensy 4.1", "isoSPI 1-2", "isoSPI 3-4", "isoSPI 5-6", "CAN1", "CAN2", "CAN3",
             "CAN4", "CAN5", "CAN6"]
    sec_origin = {}
    for i, g in enumerate(order):
        sec_origin[g] = (col_x[i % 4], 30.0 + (i // 4) * 270.0)
    texts = []
    for g in order:
        x0, y0 = sec_origin[g]
        texts.append('(text %s (exclude_from_sim no) (at %s %s 0) (effects (font (size 3 3) (thickness 0.5) (bold yes)) '
                     '(justify left bottom)) (uuid %s))' % (q(g), fmt(x0), fmt(y0 - 6), uid("sectxt", g)))
        texts.append('(rectangle (start %s %s) (end %s %s) (stroke (width 0.2) (type dash)) (fill (type none)) (uuid %s))'
                     % (fmt(x0 - 6), fmt(y0 - 14), fmt(x0 + sec_w - 14), fmt(y0 + 250), uid("secbox", g)))
        cursor[g] = [x0 + 30.0, y0 + 8.0, 0.0]   # x, y, row height

    def snap(v):
        return round(v / 1.27) * 1.27

    wires, labels, ncs, syms = [], [], [], []

    def place(p, ref, symname, pins_nets, value, fpid, mpn, lcsc, in_bom=True, on_board=True, dnp=False):
        g = p["group"]
        w, h = symbol_extent(symname)
        cx, cy, rowh = cursor[g]
        x0, _ = sec_origin[g]
        span = w + 48.0
        if cx + span > x0 + sec_w - 10:
            cx = x0 + 30.0
            cy += rowh + 11.0
            rowh = 0.0
        sx, sy = snap(cx + w / 2.0), snap(cy + h / 2.0)
        cursor[g] = [cx + span, cy, max(rowh, h)]
        su = uid("sym", ref)
        props = []
        props.append('(property "Reference" %s (at %s %s 0) (effects (font (size 1.1 1.1))))' % (q(ref), fmt(sx), fmt(sy - h / 2.0 - 1.5)))
        props.append('(property "Value" %s (at %s %s 0) (effects (font (size 1.1 1.1))))' % (q(value), fmt(sx), fmt(sy + h / 2.0 + 1.5)))
        props.append('(property "Footprint" %s (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (q(fpid), fmt(sx), fmt(sy)))
        props.append('(property "Datasheet" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (fmt(sx), fmt(sy)))
        props.append('(property "Description" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (fmt(sx), fmt(sy)))
        if mpn is not None:
            props.append('(property "MPN" %s (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (q(mpn), fmt(sx), fmt(sy)))
            props.append('(property "JLCPCB Part #" %s (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (q(lcsc), fmt(sx), fmt(sy)))
        pin_uuids = " ".join('(pin %s (uuid %s))' % (q(num), uid("pin", ref, num)) for num in symbol_pins(symname))
        syms.append('(symbol (lib_id %s) (at %s %s 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp %s) (uuid %s)\n  %s\n  %s\n'
                    '  (instances (project %s (path %s (reference %s) (unit 1)))))'
                    % (q("T41:" + symname), fmt(sx), fmt(sy), "yes" if in_bom else "no", "yes" if on_board else "no",
                       "yes" if dnp else "no", su, "\n  ".join(props), pin_uuids, q(NAME), q("/" + ROOT_UUID), q(ref)))
        for num, (px, py, side) in symbol_pins(symname).items():
            ax, ay = sx + px, sy - py
            net = pins_nets.get(num, D.NC)
            if net is D.NC:
                ncs.append('(no_connect (at %s %s) (uuid %s))' % (fmt(ax), fmt(ay), uid("nc", ref, num)))
                continue
            if side == "L":
                bx, by, ang, just = ax - 3.81, ay, 0, "right"
            elif side == "R":
                bx, by, ang, just = ax + 3.81, ay, 0, "left"
            else:
                bx, by, ang, just = ax, ay + 3.81, 270, "right"
            wires.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'
                         % (fmt(ax), fmt(ay), fmt(bx), fmt(by), uid("w", ref, num)))
            labels.append('(label %s (at %s %s %d) (effects (font (size 1.0 1.0)) (justify %s bottom)) (uuid %s))'
                          % (q(net), fmt(bx), fmt(by), ang, just, uid("l", ref, num)))
        return su

    sym_uuid = {}
    for p in D.parts:
        val, mpn, mfr, lcsc, lib, fp, asm = D.PARTS[p["part"]]
        mpn_out = mpn if asm != "NONE" else None
        in_bom = asm != "NONE"
        sym_uuid[p["ref"]] = place(p, p["ref"], p["sym"], p["pins"], part_value(p), "%s:%s" % (lib, fp),
                                   mpn_out, lcsc, in_bom=in_bom)
    # Power flags
    for i, net in enumerate(sorted(set(D.flags))):
        g = "Power and USB" if not D.can_domain(net) else "CAN%d" % D.can_domain(net)
        fake = dict(group=g)
        ref = "#FLG%02d" % (i + 1)
        w, h = symbol_extent("flag")
        cx, cy, rowh = cursor[g]
        x0, _ = sec_origin[g]
        if cx + 40 > x0 + sec_w - 10:
            cx = x0 + 30.0
            cy += rowh + 11.0
            rowh = 0.0
        sx, sy = snap(cx + 5), snap(cy + 5)
        cursor[g] = [cx + 40.0, cy, max(rowh, h)]
        syms.append('(symbol (lib_id "T41:flag") (at %s %s 0) (unit 1) (exclude_from_sim no) (in_bom no) (on_board no) (dnp no) (uuid %s)\n'
                    '  (property "Reference" %s (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
                    '  (property "Value" "PWR_FLAG" (at %s %s 0) (effects (font (size 1.1 1.1))))\n'
                    '  (property "Footprint" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
                    '  (pin "1" (uuid %s))\n'
                    '  (instances (project %s (path %s (reference %s) (unit 1)))))'
                    % (fmt(sx), fmt(sy), uid("flag", net), q(ref), fmt(sx), fmt(sy - 5), fmt(sx), fmt(sy - 7), fmt(sx), fmt(sy),
                       uid("flagpin", net), q(NAME), q("/" + ROOT_UUID), q(ref)))
        wires.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))'
                     % (fmt(sx), fmt(sy), fmt(sx), fmt(sy + 3.81), uid("fw", net)))
        labels.append('(label %s (at %s %s 270) (effects (font (size 1.0 1.0)) (justify right bottom)) (uuid %s))'
                      % (q(net), fmt(sx), fmt(sy + 3.81), uid("fl", net)))

    notes = [
        "Teensy 4.1 sits in J2/J3 (8.5 mm sockets). Cut the VIN-VUSB pads on the Teensy so USB power enters only through J1/F1/D2.",
        "J4/J5 pogo pins reach the Teensy USB device D-/D+ pads under the module; the carrier USB-C carries data and power.",
        "CAN1-3 use Teensy FlexCAN1-3; CAN4-6 use MCP2518FD on SPI1. Each CAN port has its own isolated supply and ground.",
        "DSUB-9 female, CiA 303-1 / PEAK pinout: 2 CAN_L, 7 CAN_H, 3 and 6 CAN_GND, 5 and shell to shield RC.",
        "isoSPI ports use SM91801AL-E (1000 V DC working, basic insulation). Keep 8 mm copper clearance per port.",
    ]
    for i, t in enumerate(notes):
        texts.append('(text %s (exclude_from_sim no) (at 896 %s 0) (effects (font (size 1.8 1.8)) (justify left bottom)) (uuid %s))'
                     % (q(t), fmt(590 + i * 6.0), uid("note", i)))

    out.extend(texts)
    out.extend(syms)
    out.extend(wires)
    out.extend(labels)
    out.extend(ncs)
    out.append('(sheet_instances (path "/" (page "1")))')
    out.append(")")
    with open(SCH, "w") as f:
        f.write("\n".join(out) + "\n")
    return sym_uuid


def write_project_files():
    src = os.path.join(REPO, "hardware", "kicad", "CAN_isoSPI_adapter.kicad_pro")
    pro = json.load(open(src))
    pro["meta"]["filename"] = NAME + ".kicad_pro"
    ds = pro["board"]["design_settings"]
    ds["rules"]["min_clearance"] = 0.15
    ds["rules"]["min_track_width"] = 0.1
    ns = pro["net_settings"]
    base = ns["classes"][0]
    base.update(dict(clearance=0.2, track_width=0.2, via_diameter=0.6, via_drill=0.3))
    power = dict(base)
    power.update(dict(name="Power", clearance=D.NETCLASS_POWER[1], track_width=D.NETCLASS_POWER[0],
                      via_diameter=0.6, via_drill=0.3, priority=0))
    hc = dict(base)
    hc.update(dict(name="HighCurrent", clearance=D.NETCLASS_HIGHCURRENT[1], track_width=D.NETCLASS_HIGHCURRENT[0],
                   via_diameter=0.8, via_drill=0.4, priority=3))
    iso = dict(base)
    iso.update(dict(name="isoSPI", clearance=0.2, track_width=0.3, priority=1))
    usb = dict(base)
    usb.update(dict(name="USB", clearance=0.2, track_width=0.3, diff_pair_width=0.3, diff_pair_gap=0.2, priority=2))
    ns["classes"] = [base, power, iso, usb, hc]
    pats = [dict(netclass="Power", pattern="/" + n) for n in sorted(D.POWER_NETS)]
    pats += [dict(netclass="HighCurrent", pattern="/" + n) for n in sorted(D.HIGH_CURRENT_NETS)]
    for p in range(1, 7):
        pats += [dict(netclass="isoSPI", pattern="/ISO%d_IP" % p), dict(netclass="isoSPI", pattern="/ISO%d_IM" % p),
                 dict(netclass="isoSPI", pattern="/ISO%dC_P" % p), dict(netclass="isoSPI", pattern="/ISO%dC_N" % p)]
    pats += [dict(netclass="USB", pattern="/USB_DP"), dict(netclass="USB", pattern="/USB_DM")]
    ns["netclass_patterns"] = pats
    ns["netclass_assignments"] = None
    pro["sheets"] = [[ROOT_UUID, "Root"]]
    pro["schematic"]["top_level_sheets"] = [dict(filename=NAME + ".kicad_sch", name=NAME, uuid=ROOT_UUID)]
    pro["boards"] = []
    json.dump(pro, open(PRO, "w"), indent=2)
    open(os.path.join(PRJ_DIR, "sym-lib-table"), "w").write(
        '(sym_lib_table (version 7) (lib (name "T41")(type "KiCad")(uri "${KIPRJMOD}/T41Carrier.kicad_sym")(options "")(descr "Teensy carrier symbols")))\n')
    open(os.path.join(PRJ_DIR, "fp-lib-table"), "w").write(
        '(fp_lib_table (version 7) (lib (name "T41")(type "KiCad")(uri "${KIPRJMOD}/T41Carrier.pretty")(options "")(descr "Teensy carrier footprints")))\n')
    write_rules()


def write_rules():
    lines = ["(version 1)",
             "# Generated by tools/generate_t41.py. Board-level insulation still needs a system review.",
             "# Each floating isoSPI cable domain keeps 8 mm copper clearance to all other copper."]
    for p in range(1, 7):
        dom = "A.NetName == '/ISO%dC_*'" % p
        oth = "B.NetName != '/ISO%dC_*' && B.NetName != 'unconnected-*'" % p
        lines.append('(rule "isoSPI port %d 8 mm"\n  (constraint clearance (min 8mm))\n  (condition "%s && %s"))' % (p, dom, oth))
    lines.append("# Each isolated CAN domain keeps 3 mm from logic copper and from the other CAN domains.")
    for n in range(1, 7):
        lines.append('(rule "CAN%d isolation 3 mm"\n  (constraint clearance (min 3mm))\n'
                     '  (condition "A.NetName == \'/CAN%dI_*\' && B.NetName != \'/CAN%dI_*\' && B.NetName != \'unconnected-*\' && B.NetName != \'\'"))'
                     % (n, n, n))
    open(os.path.join(PRJ_DIR, NAME + ".kicad_dru"), "w").write("\n".join(lines) + "\n")


# =============================================================================
# PCB
# =============================================================================
def mm(v):
    import pcbnew
    return pcbnew.FromMM(v)


def pt(x, y):
    import pcbnew
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


def fp_path(lib):
    if lib == D.LOC:
        return os.path.join(PRJ_DIR, "T41Carrier.pretty")
    return os.path.join(KICAD_FP, lib + ".pretty")


MODELS = {
    "ADBMS6822_05-08-7057": "ADBMS6822_05-08-7057.wrl",
    "EG1218": "EG1218.wrl",
    "SM91801AL-E": "SM91801AL-E.wrl",
    "WE_760390014": "WE_760390014.wrl",
    "Pogo_YTC1P-8535_D2.0mm": "Pogo_YTC1P-8535.wrl",
}


def add_line(board, layer, a, b, width=0.12):
    import pcbnew
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(*a))
    s.SetEnd(pt(*b))
    s.SetLayer(layer)
    s.SetWidth(mm(width))
    board.Add(s)


def add_text(board, text, x, y, size=1.2, layer=None, rot=0, bold=False, just=0):
    import pcbnew
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pt(x, y))
    t.SetLayer(pcbnew.F_SilkS if layer is None else layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * (0.2 if bold else 0.15)))
    t.SetTextAngleDegrees(rot)
    if just < 0:
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    elif just > 0:
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    board.Add(t)


def make_zone(board, net, layers, poly, name, priority=0, rule=False):
    import pcbnew
    z = pcbnew.ZONE(board)
    if len(layers) == 1:
        z.SetLayer(layers[0])
    ls = pcbnew.LSET()
    for L in layers:
        ls.AddLayer(L)
    z.SetLayerSet(ls)
    o = z.Outline()
    o.NewOutline()
    for x, y in poly:
        o.Append(mm(OX + x), mm(OY + y))
    z.SetZoneName(name)
    if rule:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
    else:
        z.SetNet(net)
        z.SetLocalClearance(mm(0.3))
        z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetAssignedPriority(priority)
    board.Add(z)
    return z


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def can_zone_rect(n):
    cx = D.CAN_CX[n - 1]
    x0 = 0.6 if n == 1 else cx - 15.0
    x1 = D.BOARD_W - 0.6 if n == 6 else cx + 15.0
    return rect(x0, D.BARRIER_Y1, x1, D.BOARD_H - 0.6)


def bottom_pours(board):
    """Bottom-layer ground pours, added after routing so they fill around tracks."""
    import pcbnew
    W = D.BOARD_W
    make_zone(board, board.FindNet("/GND"), [pcbnew.B_Cu], rect(0.6, D.ISO_BAND_Y, W - 0.6, D.BARRIER_Y0), "GND_B")
    make_zone(board, board.FindNet("/+5V"), [pcbnew.In3_Cu], rect(0.6, D.ISO_BAND_Y, W - 0.6, D.BARRIER_Y0), "+5V_In3")
    for n in range(1, 7):
        make_zone(board, board.FindNet("/CAN%dI_GND" % n), [pcbnew.B_Cu], can_zone_rect(n), "CAN%d_ISO_GND_B" % n)


def build_pcb(sym_uuid):
    import pcbnew
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(6)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_SIGNAL)
    board.SetLayerType(pcbnew.In3_Cu, pcbnew.LT_SIGNAL)
    board.SetLayerType(pcbnew.In4_Cu, pcbnew.LT_POWER)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.1)
    ds.m_MinClearance = mm(0.15)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.5)
    ds.SetAuxOrigin(pt(0, D.BOARD_H))
    ds.SetGridOrigin(pt(0, D.BOARD_H))
    tb = board.GetTitleBlock()
    tb.SetTitle(D.TITLE)
    tb.SetRevision(D.REV)
    tb.SetDate(D.DATE)
    tb.SetComment(0, "Prototype / bench validation pending")

    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    for p in D.parts:
        val, mpn, mfr, lcsc, lib, fpn, asm = D.PARTS[p["part"]]
        fp = pcbnew.FootprintLoad(fp_path(lib), fpn)
        if fp is None:
            raise SystemExit("footprint not found: %s:%s" % (lib, fpn))
        fp.SetFPID(pcbnew.LIB_ID(lib, fpn))
        fp.SetReference(p["ref"])
        fp.SetValue(part_value(p))
        if asm != "NONE":
            for fname, ftext in (("MPN", mpn), ("JLCPCB Part #", lcsc)):
                fp.SetField(fname, ftext)
                fld = fp.GetField(fname)
                fld.SetVisible(False)
                fld.SetLayer(pcbnew.F_Fab)
        fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuid[p["ref"]]))
        fp.SetSheetname("Root")
        fp.SetSheetfile(NAME + ".kicad_sch")
        if fpn in MODELS:
            m = pcbnew.FP_3DMODEL()
            m.m_Filename = "${KIPRJMOD}/../kicad/models/" + MODELS[fpn]
            fp.Models().push_back(m)
        if fpn == "USB_C_Receptacle_HRO_TYPE-C-31-M-12":
            # KiCad 10 ships no model for this footprint; use the drawn envelope.
            fp.Models().clear()
            m = pcbnew.FP_3DMODEL()
            m.m_Filename = "${KIPRJMOD}/../kicad/models/USB_C_HRO_TYPE-C-31-M-12.wrl"
            fp.Models().push_back(m)
        if p["ref"] == "J2":
            # Visual Teensy 4.1 module; origin at J2 pin 1 (see make_visual_models.py)
            m = pcbnew.FP_3DMODEL()
            m.m_Filename = "${KIPRJMOD}/../kicad/models/Teensy41-mounted.wrl"
            fp.Models().push_back(m)
        x, y, rot = p["pos"]
        fp.SetPosition(pt(x, y))
        fp.SetOrientationDegrees(rot)
        names = symbol_pin_names(p["sym"])
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num == "":
                continue
            if num not in names:
                continue
            nn = p["pins"].get(num, D.NC)
            if nn is D.NC:
                nn = unconnected_name(p["ref"], names[num], num)
            else:
                nn = "/" + nn
            pad.SetNet(net(nn))
        if asm == "NONE" and p["sym"] == "hole":
            fp.SetBoardOnly(False)
        board.Add(fp)
        # keep reference text small and readable
        # Reference designators live on the fabrication layer (assembly drawing);
        # the silkscreen carries functional labels only.
        r = fp.Reference()
        r.SetLayer(pcbnew.F_Fab)
        r.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        r.SetTextThickness(mm(0.12))

    # Board outline with rounded corners
    W, H, Rr = D.BOARD_W, D.BOARD_H, D.CORNER_R
    E = pcbnew.Edge_Cuts
    add_line(board, E, (Rr, 0), (W - Rr, 0), 0.05)
    add_line(board, E, (W, Rr), (W, H - Rr), 0.05)
    add_line(board, E, (W - Rr, H), (Rr, H), 0.05)
    add_line(board, E, (0, H - Rr), (0, Rr), 0.05)
    for cx, cy, a0 in ((Rr, Rr, 180), (W - Rr, Rr, 270), (W - Rr, H - Rr, 0), (Rr, H - Rr, 90)):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        pts = []
        for a in (a0, a0 + 45, a0 + 90):
            pts.append(pt(cx + Rr * math.cos(math.radians(a)), cy + Rr * math.sin(math.radians(a))))
        s.SetArcGeometry(pts[0], pts[1], pts[2])
        s.SetLayer(E)
        s.SetWidth(mm(0.05))
        board.Add(s)

    # Copper zones
    L1, L2, LB = pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
    logic = rect(0.6, D.ISO_BAND_Y, W - 0.6, D.BARRIER_Y0)
    L4 = pcbnew.In4_Cu
    make_zone(board, net("/GND"), [L1, L4], logic, "GND")
    for n in range(1, 7):
        make_zone(board, net("/CAN%dI_GND" % n), [L1, L4], can_zone_rect(n), "CAN%d_ISO_GND" % n)

    # isoSPI cable-domain tracks (short, straight, 0.8 mm)
    for p in range(1, 7):
        xp = D.PORT_X[p - 1]
        for dx, nn in ((-2.54, "/ISO%dC_P" % p), (2.54, "/ISO%dC_N" % p)):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pt(xp + dx, D.ISO_T_Y - 6.35))
            t.SetEnd(pt(xp + dx, D.TERM_Y))
            t.SetWidth(mm(0.8))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(net(nn))
            board.Add(t)

    silkscreen(board)
    fanout(board)
    qfn_fanout(board)
    pcbnew.SaveBoard(PCB, board)
    return board


def silkscreen(board):
    import pcbnew
    S = pcbnew.F_SilkS
    W, H = D.BOARD_W, D.BOARD_H
    # isoSPI port labels
    for p in range(1, 7):
        xp = D.PORT_X[p - 1]
        add_text(board, "isoSPI %d" % p, xp + 7.5, 9.0, 1.2, rot=90, bold=True)
        add_text(board, "+", xp - 5.4, 13.65, 1.2)
        add_text(board, "-", xp + 5.4, 13.65, 1.2)
    add_text(board, "8 mm isoSPI barrier: no copper between ports", W / 2.0, D.ISO_BAND_Y - 1.2, 0.9)
    # CAN labels
    names = ["CAN1 FlexCAN1", "CAN2 FlexCAN2", "CAN3 FlexCAN3 FD", "CAN4 MCP2518FD", "CAN5 MCP2518FD", "CAN6 MCP2518FD"]
    for n in range(1, 7):
        cx = D.CAN_CX[n - 1]
        add_text(board, "CAN%d" % n, cx + 2.5, 86.0, 1.2, rot=90, bold=True)
        add_text(board, "120R", cx - 8.5, 100.8, 0.8)
        add_text(board, "OFF", cx - 3.5, 100.8, 0.8)
        add_text(board, "PWR", cx - 14.0, 100.4, 0.8)
    for n in range(1, 6):
        x = (D.CAN_CX[n - 1] + D.CAN_CX[n]) / 2.0
        for y0 in range(int(D.BARRIER_Y1) + 1, int(H) - 14, 3):
            add_line(board, S, (x, y0), (x, y0 + 1.5), 0.12)
    # Teensy outline and notes
    x1 = D.TEENSY_X1 - 1.27
    x2 = x1 + 60.96
    y1 = D.TEENSY_YC - 8.89
    y2 = D.TEENSY_YC + 8.89
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        add_line(board, pcbnew.F_Fab, a, b, 0.1)
    add_text(board, "< USB END   TEENSY 4.1", 44.0, D.TEENSY_YC - 1.0, 1.0)
    add_text(board, "CUT VIN-VUSB ON TEENSY", 48.0, D.TEENSY_YC - 3.0, 0.8)
    add_text(board, "USB-C", 6.0, D.TEENSY_YC - 6.8, 0.9)
    add_text(board, "5V", 7.0, 76.0, 0.8)
    add_text(board, "OK", 89.0, 50.0, 0.8)
    add_text(board, "ERR", 89.5, 54.0, 0.8)
    for x, y, t in ((92.0, 48.0, "5V"), (96.0, 48.0, "GND"), (100.0, 48.0, "3V3"), (92.0, 57.2, "FLT"), (96.0, 57.2, "D32")):
        add_text(board, t, x, y, 0.8)
    add_text(board, D.TITLE, 160.0, 50.0, 1.6, bold=True)
    add_text(board, "%s %s  %s" % (D.PROJECT, D.REV, D.DATE), 160.0, 53.5, 1.0)
    add_text(board, "Prototype - insulation not certified", 160.0, 56.5, 0.9)
    add_text(board, "Channel N = CAN N (bottom) + isoSPI N (top), numbered left to right", 160.0, 59.5, 0.9)


# =============================================================================
# Routing
# =============================================================================
def routing_keepouts(board):
    import pcbnew
    W, H = D.BOARD_W, D.BOARD_H
    allcu = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu]
    zs = []
    # isoSPI band: everything except the six port windows
    edges = [0.0]
    for xp in D.PORT_X:
        edges += [xp - 6.0, xp + 6.0]
    edges.append(W)
    for i in range(0, len(edges), 2):
        if edges[i + 1] - edges[i] > 0.5:
            zs.append(make_zone(board, None, allcu, rect(edges[i], 0.0, edges[i + 1], 17.0), "ko", rule=True))
    zs.append(make_zone(board, None, allcu, rect(0.0, 16.5, W, D.ISO_BAND_Y), "ko", rule=True))
    # CAN barrier band and the gaps between isolated columns
    zs.append(make_zone(board, None, allcu, rect(0.0, D.BARRIER_Y0, W, D.BARRIER_Y1), "ko", rule=True))
    for n in range(1, 6):
        x = (D.CAN_CX[n - 1] + D.CAN_CX[n]) / 2.0
        zs.append(make_zone(board, None, allcu, rect(x - 1.6, D.BARRIER_Y0, x + 1.6, H), "ko", rule=True))
    return zs


PLANE_NETS = {"/GND": "logic"}
PLANE_NETS.update({"/CAN%dI_GND" % n: n for n in range(1, 7)})
VIA_D, VIA_DRILL, STUB_W, CLR = 0.6, 0.3, 0.3, 0.25


def plane_region_ok(region, x, y):
    if region == "logic":
        return D.ISO_BAND_Y + 0.8 <= y <= D.BARRIER_Y0 - 0.8 and 1.2 <= x <= D.BOARD_W - 1.2
    pts = can_zone_rect(region)
    return pts[0][0] + 0.8 <= x <= pts[1][0] - 0.8 and D.BARRIER_Y1 + 0.8 <= y <= D.BOARD_H - 1.2


def fanout(board):
    """Connect every SMD pad of a plane net to its inner-layer plane with a stub and via.

    Planes are added back as zones; the autorouter only sees signal nets.
    Returns the list of pads that could not be fanned out.
    """
    import pcbnew
    F = pcbnew.F_Cu
    obstacles = []      # (netcode, shape, layer or None for all layers)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            for L in (pcbnew.F_Cu, pcbnew.B_Cu):
                if pad.IsOnLayer(L):
                    obstacles.append((pad.GetNetCode(), pad.GetEffectiveShape(L), L))
            if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                obstacles.append((pad.GetNetCode() if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else -1,
                                  pad.GetEffectiveHoleShape(), None))
    for t in board.GetTracks():
        obstacles.append((t.GetNetCode(), t.GetEffectiveShape(t.GetLayer()), t.GetLayer()))
    keep = []
    W, H = D.BOARD_W, D.BOARD_H
    for xp in D.PORT_X:
        keep.append((xp - 6.0, 0.0, xp + 6.0, 17.0))
    keep.append((0.0, 0.0, W, D.ISO_BAND_Y))
    keep.append((0.0, D.BARRIER_Y0, W, D.BARRIER_Y1))
    for n in range(1, 6):
        x = (D.CAN_CX[n - 1] + D.CAN_CX[n]) / 2.0
        keep.append((x - 1.6, D.BARRIER_Y0, x + 1.6, H))

    def in_keepout(x, y, r):
        return any(a - r < x < c + r and b - r < y < d + r for a, b, c, d in keep)

    def free(netcode, shape, layer, clr):
        for nc, s, L in obstacles:
            if nc == netcode and nc > 0:
                continue
            if layer is not None and L is not None and L != layer:
                continue
            if shape.Collide(s, mm(clr)):
                return False
        return True

    def lc(v):
        return (pcbnew.ToMM(v.x) - OX, pcbnew.ToMM(v.y) - OY)

    failed, added = [], 0
    seen = set()
    for fp in board.GetFootprints():
        fc = fp.GetPosition()
        pads = list(fp.Pads())
        for pad in pads:
            name = pad.GetNetname()
            if name not in PLANE_NETS or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or not pad.IsOnLayer(F):
                continue
            nc = pad.GetNetCode()
            region = PLANE_NETS[name]
            c = pad.GetPosition()
            key = (fp.GetReference(), nc, c.x, c.y)
            if key in seen:      # stacked pads (USB-C A1/B12) share one fanout
                continue
            seen.add(key)
            size = pad.GetSize()
            big = min(pcbnew.ToMM(size.x), pcbnew.ToMM(size.y)) >= 1.6
            done = False
            if big:   # exposed pad / large pad: vias inside the pad
                n_ok = 0
                ex, ey = pcbnew.ToMM(size.x), pcbnew.ToMM(size.y)
                offs = [(0, 0)] if max(ex, ey) < 2.0 else [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]
                for dx, dy in offs:
                    x, y = lc(c)
                    x, y = x + dx, y + dy
                    v = pcbnew.SHAPE_SEGMENT(pt(x, y), pt(x, y), mm(VIA_D))
                    if plane_region_ok(region, x, y) and free(nc, v, None, CLR):
                        via = pcbnew.PCB_VIA(board)
                        via.SetPosition(pt(x, y))
                        via.SetWidth(mm(VIA_D))
                        via.SetDrill(mm(VIA_DRILL))
                        via.SetNet(pad.GetNet())
                        board.Add(via)
                        obstacles.append((nc, pcbnew.SHAPE_SEGMENT(pt(x, y), pt(x, y), mm(VIA_D)), None))
                        n_ok += 1
                done = n_ok > 0
            if not done:
                # QFN pin next to a same-net exposed pad: short stub to the pad
                ep = [p for p in pads if p is not pad and p.GetNetCode() == nc and
                      min(pcbnew.ToMM(p.GetSize().x), pcbnew.ToMM(p.GetSize().y)) >= 1.6]
                if ep and fp.GetValue().startswith("ADBMS"):
                    # Straight inward along the pad axis into the exposed pad, or for
                    # corner pins inward past the pad row and then to the EP corner.
                    e = ep[0].GetPosition()
                    eh = int(min(ep[0].GetSize().x, ep[0].GetSize().y) // 2 - mm(0.2))
                    dx, dy = e.x - c.x, e.y - c.y
                    bb = pad.GetBoundingBox()
                    horiz = bb.GetWidth() > bb.GetHeight()
                    paths = []
                    if horiz and abs(dy) < eh:
                        paths.append([c, pcbnew.VECTOR2I(e.x - (eh if dx > 0 else -eh), c.y)])
                    if not horiz and abs(dx) < eh:
                        paths.append([c, pcbnew.VECTOR2I(c.x, e.y - (eh if dy > 0 else -eh))])
                    step = int(mm(0.85))
                    if horiz:
                        m = pcbnew.VECTOR2I(c.x + (step if dx > 0 else -step), c.y)
                    else:
                        m = pcbnew.VECTOR2I(c.x, c.y + (step if dy > 0 else -step))
                    corner = pcbnew.VECTOR2I(e.x + (eh if c.x > e.x else -eh), e.y + (eh if c.y > e.y else -eh))
                    paths.append([c, m, corner])
                    for path in paths:
                        segs = [pcbnew.SHAPE_SEGMENT(path[i], path[i + 1], mm(0.18)) for i in range(len(path) - 1)]
                        if all(free(nc, sg, F, 0.205) for sg in segs):
                            for i in range(len(path) - 1):
                                t = pcbnew.PCB_TRACK(board)
                                t.SetStart(path[i])
                                t.SetEnd(path[i + 1])
                                t.SetWidth(mm(0.18))
                                t.SetLayer(F)
                                t.SetNet(pad.GetNet())
                                board.Add(t)
                            obstacles.extend((nc, sg, F) for sg in segs)
                            done = True
                            break
            if not done:
                px, py = lc(c)
                fx, fy = lc(fc)
                ax, ay = px - fx, py - fy
                n0 = math.hypot(ax, ay) or 1.0
                fine = min(pcbnew.ToMM(size.x), pcbnew.ToMM(size.y)) < 0.4
                sw, sclr = (0.2, 0.2) if fine else (STUB_W, CLR)
                dirs = []
                if fine:
                    # straight out along the pad's long axis, away from the package
                    bb = pad.GetBoundingBox()
                    horiz = bb.GetWidth() > bb.GetHeight()
                    if horiz:
                        dirs.append((1.0 if ax > 0 else -1.0, 0.0))
                    else:
                        dirs.append((0.0, 1.0 if ay > 0 else -1.0))
                dirs.append((ax / n0, ay / n0))
                for k in range(16):
                    a = math.radians(k * 22.5)
                    dirs.append((math.cos(a), math.sin(a)))
                half = max(pcbnew.ToMM(size.x), pcbnew.ToMM(size.y)) / 2.0
                for dist in [half + 0.55 + 0.25 * i for i in range(10)]:
                    for dx, dy in dirs:
                        x, y = px + dx * dist, py + dy * dist
                        if not plane_region_ok(region, x, y) or in_keepout(x, y, 0.5):
                            continue
                        v = pcbnew.SHAPE_SEGMENT(pt(x, y), pt(x, y), mm(VIA_D))
                        seg = pcbnew.SHAPE_SEGMENT(c, pt(x, y), mm(sw))
                        if free(nc, v, None, CLR) and free(nc, seg, F, sclr):
                            t = pcbnew.PCB_TRACK(board)
                            t.SetStart(c)
                            t.SetEnd(pt(x, y))
                            t.SetWidth(mm(sw))
                            t.SetLayer(F)
                            t.SetNet(pad.GetNet())
                            board.Add(t)
                            via = pcbnew.PCB_VIA(board)
                            via.SetPosition(pt(x, y))
                            via.SetWidth(mm(VIA_D))
                            via.SetDrill(mm(VIA_DRILL))
                            via.SetNet(pad.GetNet())
                            board.Add(via)
                            obstacles.append((nc, seg, F))
                            obstacles.append((nc, v, None))
                            done = True
                            break
                    if done:
                        break
            if done:
                added += 1
            else:
                failed.append("%s.%s %s" % (fp.GetReference(), pad.GetNumber(), name))
    print("fanout: %d pads connected, %d failed %s" % (added, len(failed), failed), flush=True)
    return failed


def qfn_fanout(board):
    """Deterministic escape for the ADBMS6822 QFNs: every non-ground signal or
    supply pin gets a straight 0.2 mm stub that fans out to a via on a 1 mm
    lateral pitch about 5 mm from the package centre."""
    import pcbnew
    F = pcbnew.F_Cu
    made, failed = 0, []
    obstacles = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.IsOnLayer(F):
                obstacles.append((pad.GetNetCode(), pad.GetEffectiveShape(F), F))
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                obstacles.append((pad.GetNetCode(), pad.GetEffectiveHoleShape(), None))
    for t in board.GetTracks():
        L = None if t.Type() == pcbnew.PCB_VIA_T else t.GetLayer()
        obstacles.append((t.GetNetCode(), t.GetEffectiveShape(F if L is None else L), L))

    def free(nc, shape, layer):
        for n, s, L in obstacles:
            if n == nc and n > 0:
                continue
            if layer is not None and L is not None and L != layer:
                continue
            if shape.Collide(s, mm(0.2)):
                return False
        return True

    for fp in board.GetFootprints():
        if not fp.GetValue().startswith("ADBMS"):
            continue
        c = fp.GetPosition()
        for pad in fp.Pads():
            name = pad.GetNetname()
            if not name or name in PLANE_NETS or name.startswith("unconnected"):
                continue
            p = pad.GetPosition()
            dx, dy = pcbnew.ToMM(p.x - c.x), pcbnew.ToMM(p.y - c.y)
            if abs(dx) < 1.2 and abs(dy) < 1.2:
                continue                       # exposed pad
            if abs(dx) > abs(dy):              # left or right side
                nx, ny, off = (1.0 if dx > 0 else -1.0), 0.0, dy
            else:
                nx, ny, off = 0.0, (1.0 if dy > 0 else -1.0), dx
            done = False
            for D, spread in [(d, f) for f in (2.0, 1.5, 2.5, 1.0) for d in (5.0, 5.4, 5.8, 6.3)]:
                ex = nx * D + (0.0 if nx else spread * off)
                ey = ny * D + (0.0 if ny else spread * off)
                v = pcbnew.VECTOR2I(c.x + mm(ex), c.y + mm(ey))
                # leave the pad row straight, then fan out
                k = pcbnew.VECTOR2I(c.x + mm(nx * 3.15 + (0.0 if nx else off)), c.y + mm(ny * 3.15 + (0.0 if ny else off)))
                segs = [pcbnew.SHAPE_SEGMENT(p, k, mm(0.2)), pcbnew.SHAPE_SEGMENT(k, v, mm(0.2))]
                seg = segs[1]
                via = pcbnew.SHAPE_SEGMENT(v, v, mm(0.6))
                nc = pad.GetNetCode()
                if all(free(nc, sg, F) for sg in segs) and free(nc, via, None):
                    for a0, a1 in ((p, k), (k, v)):
                        t = pcbnew.PCB_TRACK(board)
                        t.SetStart(a0)
                        t.SetEnd(a1)
                        t.SetWidth(mm(0.2))
                        t.SetLayer(F)
                        t.SetNet(pad.GetNet())
                        board.Add(t)
                    obstacles.append((nc, segs[0], F))
                    vv = pcbnew.PCB_VIA(board)
                    vv.SetPosition(v)
                    vv.SetWidth(mm(0.6))
                    vv.SetDrill(mm(0.3))
                    vv.SetNet(pad.GetNet())
                    board.Add(vv)
                    obstacles.append((nc, seg, F))
                    obstacles.append((nc, via, None))
                    made += 1
                    done = True
                    break
            if not done:
                failed.append("%s.%s" % (fp.GetReference(), pad.GetNumber()))
    print("qfn fanout: %d pins, failed %s" % (made, failed), flush=True)


def split_plane_nets(board):
    """Give every plane-net pad (with its fanout) a private net so the router ignores it."""
    import pcbnew
    conn = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = pad.GetNetname()
            if name in PLANE_NETS:
                nn = pcbnew.NETINFO_ITEM(board, "%s~~%s_%s_%d" % (name, fp.GetReference(), pad.GetNumber(), len(conn)))
                board.Add(nn)
                conn[(fp.GetReference(), pad.GetNumber(), len(conn))] = (pad, nn)
    items = list(board.GetTracks())
    for (ref, num, _), (pad, nn) in conn.items():
        old = pad.GetNetCode()
        c = pad.GetPosition()
        frontier = [c]
        while frontier:
            pnt = frontier.pop()
            for t in items:
                if t.GetNetCode() != old:
                    continue
                if t.Type() == pcbnew.PCB_TRACE_T and t.GetStart() == pnt:
                    t.SetNet(nn)
                    frontier.append(t.GetEnd())
                elif t.Type() == pcbnew.PCB_VIA_T and t.GetPosition() == pnt:
                    t.SetNet(nn)
        for t in items:
            if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == old and pad.HitTest(t.GetPosition()):
                t.SetNet(nn)
        pad.SetNet(nn)


def strip_dsn_layers(path, drop=("In1.Cu", "In4.Cu")):
    """Remove the ground-plane layers from a Specctra file so the router cannot use them.

    Freerouting ignores the 'power' layer type, so the layers, their padstack
    shapes and keepouts are deleted outright. Vias still come back as through
    vias and the plane zones are filled afterwards.
    """
    text = open(path).read()
    tokens, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in "()":
            tokens.append(ch)
            i += 1
        elif ch.isspace():
            i += 1
        elif ch == '"':
            j = text.index('"', i + 1)
            tokens.append(text[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            tokens.append(text[i:j])
            i = j
    pos = 0

    def parse():
        nonlocal pos
        assert tokens[pos] == "("
        pos += 1
        node = []
        while tokens[pos] != ")":
            if tokens[pos] == "(":
                node.append(parse())
            else:
                node.append(tokens[pos])
                pos += 1
        pos += 1
        return node

    tree = parse()

    def mentions(node):
        return any((isinstance(x, str) and x in drop) or (isinstance(x, list) and mentions(x)) for x in node)

    def filt(node):
        out = []
        for x in node:
            if isinstance(x, list):
                if x and x[0] == "layer" and len(x) > 1 and x[1] in drop:
                    continue
                if x and x[0] in ("shape", "keepout", "wire_keepout", "via_keepout", "plane", "wire") and mentions(x):
                    continue
                out.append(filt(x))
            else:
                out.append(x)
        return out

    def dump(node, depth=0):
        parts = []
        for x in node:
            parts.append(dump(x, depth + 1) if isinstance(x, list) else x)
        return "(" + " ".join(parts) + ")"

    open(path, "w").write(dump(filt(tree)) + "\n")


def route(passes=40):
    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    split_plane_nets(board)
    for z in [z for z in board.Zones() if not z.GetIsRuleArea()]:
        board.Delete(z)
    routing_keepouts(board)
    dsn = os.path.join(PRJ_DIR, "build", NAME + ".dsn")
    ses = os.path.join(PRJ_DIR, "build", NAME + ".ses")
    os.makedirs(os.path.dirname(dsn), exist_ok=True)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit("DSN export failed")
    strip_dsn_layers(dsn)
    java = os.environ.get("JAVA", "java")
    jar = os.environ.get("FREEROUTING_JAR")
    if not jar:
        raise SystemExit("set FREEROUTING_JAR")
    cmd = [java, "-jar", jar, "-de", dsn, "-do", ses, "-mp", str(passes), "-mt", "6", "--gui.enabled=false"]
    print(" ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    if not pcbnew.ImportSpecctraSES(board, ses):
        raise SystemExit("SES import failed")
    # Copy the routed copper back onto the real board, restoring plane net names.
    final = pcbnew.LoadBoard(PCB)
    for t in list(final.GetTracks()):
        final.Delete(t)
    for t in board.GetTracks():
        name = t.GetNetname().split("~~")[0]
        net = final.FindNet(name)
        if t.Type() == pcbnew.PCB_VIA_T:
            n = pcbnew.PCB_VIA(final)
            n.SetPosition(t.GetPosition())
            n.SetWidth(t.GetWidth(pcbnew.F_Cu))
            n.SetDrill(t.GetDrillValue())
        else:
            n = pcbnew.PCB_TRACK(final)
            n.SetStart(t.GetStart())
            n.SetEnd(t.GetEnd())
            n.SetWidth(t.GetWidth())
            n.SetLayer(t.GetLayer())
        n.SetNet(net)
        final.Add(n)
    pcbnew.SaveBoard(PCB, final)


def finish():
    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    j1 = board.FindFootprintByReference("J1")
    if j1 and not any("USB_C_HRO" in m.m_Filename for m in j1.Models()):
        j1.Models().clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = "${KIPRJMOD}/../kicad/models/USB_C_HRO_TYPE-C-31-M-12.wrl"
        j1.Models().push_back(m)
    if not any(z.GetZoneName() == "GND_B" for z in board.Zones()):
        bottom_pours(board)
    # Teensy socket ground pins sit between dense escapes; connect them solidly to the planes.
    for ref in ("J2", "J3"):
        for pad in board.FindFootprintByReference(ref).Pads():
            if pad.GetNetname() == "/GND":
                pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
    for t in list(board.GetTracks()):
        if t.Type() == pcbnew.PCB_TRACE_T and t.GetLength() < mm(0.005):
            board.Delete(t)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)


def kicad_drc(path):
    out = os.path.join(PRJ_DIR, "build", "patch-drc.json")
    cli = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    subprocess.run([cli, "pcb", "drc", "--format", "json", "-o", out, path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return json.load(open(out))


def patch():
    """Close connections the autorouter left open and delete dangling vias.

    Each open pair gets a stub and via at both ends and a straight or L-shaped
    link on an inner signal layer or B.Cu, accepted only with 0.2 mm clearance.
    """
    import pcbnew
    finish()
    rep = kicad_drc(PCB)
    board = pcbnew.LoadBoard(PCB)
    W = 0.2
    layers = [pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.B_Cu]

    def obstacles_for(netcode):
        obs = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                for L in [pcbnew.F_Cu] + layers + [pcbnew.In1_Cu, pcbnew.In4_Cu]:
                    if pad.IsOnLayer(L) and pad.GetNetCode() != netcode:
                        obs.append((pad.GetEffectiveShape(L), L))
                if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) and pad.GetNetCode() != netcode:
                    obs.append((pad.GetEffectiveHoleShape(), None))
        for t in board.GetTracks():
            if t.GetNetCode() == netcode:
                continue
            if t.Type() == pcbnew.PCB_VIA_T:
                obs.append((pcbnew.SHAPE_SEGMENT(t.GetPosition(), t.GetPosition(), t.GetWidth(pcbnew.F_Cu)), None))
            else:
                obs.append((t.GetEffectiveShape(t.GetLayer()), t.GetLayer()))
        # Pours on In3/B.Cu are refilled afterwards, so they are not obstacles.
        return obs

    def clear(obs, shape, layer):
        for s, L in obs:
            if layer is not None and L is not None and L != layer:
                continue
            try:
                hit = shape.Collide(s, mm(0.2))
            except TypeError:
                hit = s.Collide(shape, mm(0.2))
            if hit:
                return False
        return True

    def access(item, other_pt, obs):
        """Ways to reach an item: (point, layers, stub segments [(a, b, layer)], needs_via)."""
        res = []
        if isinstance(item, pcbnew.PAD):
            c = item.GetPosition()
            res_layers = [L for L in layers if item.IsOnLayer(L)]
            if res_layers:
                res.append((c, res_layers, [], False))
            for d in [0.9 + 0.25 * i for i in range(21)]:
                for k in range(16):
                    a = math.radians(k * 22.5)
                    v = pcbnew.VECTOR2I(c.x + mm(d * math.cos(a)), c.y + mm(d * math.sin(a)))
                    res.append((v, layers, [(c, v, pcbnew.F_Cu)], True))
        else:
            ends = [item.GetStart(), item.GetEnd()]
            e = min(ends, key=lambda p: (p.x - other_pt.x) ** 2 + (p.y - other_pt.y) ** 2)
            L0 = item.GetLayer()
            if L0 in layers:
                res.append((e, [L0], [], False))
            for d in [0.9 + 0.25 * i for i in range(21)]:
                for k in range(16):
                    a = math.radians(k * 22.5)
                    v = pcbnew.VECTOR2I(e.x + mm(d * math.cos(a)), e.y + mm(d * math.sin(a)))
                    res.append((v, layers, [(e, v, L0)], True))
        return res

    def ok_access(acc, obs):
        p, ls, stubs, via = acc
        if via and not clear(obs, pcbnew.SHAPE_SEGMENT(p, p, mm(0.6)), None):
            return False
        return all(clear(obs, pcbnew.SHAPE_SEGMENT(a, b, mm(W)), L) for a, b, L in stubs)

    def find_item(desc, pos):
        p = pcbnew.VECTOR2I(mm(pos["x"]), mm(pos["y"]))
        if desc.startswith("Pad"):
            num = desc.split()[1]
            ref = desc.split(" of ")[1].split()[0]
            fp = board.FindFootprintByReference(ref)
            return [pd for pd in fp.Pads() if pd.GetNumber() == num][0]
        best = None
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T:
                continue
            for e in (t.GetStart(), t.GetEnd()):
                dd = (e.x - p.x) ** 2 + (e.y - p.y) ** 2
                if best is None or dd < best[0]:
                    best = (dd, t)
        return best[1]

    fixed = 0
    for u in rep.get("unconnected_items", []):
        a = find_item(u["items"][0]["description"], u["items"][0]["pos"])
        b = find_item(u["items"][1]["description"], u["items"][1]["pos"])
        netcode = a.GetNetCode()
        obs = obstacles_for(netcode)
        pa = a.GetPosition() if isinstance(a, pcbnew.PAD) else a.GetStart()
        pb = b.GetPosition() if isinstance(b, pcbnew.PAD) else b.GetStart()
        A = [x for x in access(a, pb, obs) if ok_access(x, obs)][:40]
        B = [x for x in access(b, pa, obs) if ok_access(x, obs)][:40]
        print("  access points: %d / %d" % (len(A), len(B)), flush=True)
        done = False
        for xa in A:
            for xb in B:
                for L in set(xa[1]) & set(xb[1]):
                    p, q = xa[0], xb[0]
                    for path in ([p, q], [p, pcbnew.VECTOR2I(p.x, q.y), q], [p, pcbnew.VECTOR2I(q.x, p.y), q]):
                        segs = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
                        if all(clear(obs, pcbnew.SHAPE_SEGMENT(s, e, mm(W)), L) for s, e in segs):
                            for s, e, LL in xa[2] + xb[2] + [(s, e, L) for s, e in segs]:
                                t = pcbnew.PCB_TRACK(board)
                                t.SetStart(s)
                                t.SetEnd(e)
                                t.SetWidth(mm(W))
                                t.SetLayer(LL)
                                t.SetNet(a.GetNet())
                                board.Add(t)
                            for x in (xa, xb):
                                if x[3]:
                                    v = pcbnew.PCB_VIA(board)
                                    v.SetPosition(x[0])
                                    v.SetWidth(mm(0.6))
                                    v.SetDrill(mm(0.3))
                                    v.SetNet(a.GetNet())
                                    board.Add(v)
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
            if done:
                break
        fixed += done
        print("patch %s: %s" % (a.GetNetname(), "connected" if done else "FAILED"), flush=True)
    removed = 0
    for v in rep.get("violations", []):
        if v["type"] != "via_dangling":
            continue
        pos = v["items"][0]["pos"]
        p = pcbnew.VECTOR2I(mm(pos["x"]), mm(pos["y"]))
        for t in list(board.GetTracks()):
            if t.Type() == pcbnew.PCB_VIA_T and abs(t.GetPosition().x - p.x) < mm(0.01) and abs(t.GetPosition().y - p.y) < mm(0.01):
                board.Delete(t)
                removed += 1
                break
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    # Trim stubs left behind by removed vias (repeat until nothing dangles).
    trimmed = 0
    for _ in range(4):
        rep = kicad_drc(PCB)
        dang = [v for v in rep.get("violations", []) if v["type"] in ("track_dangling", "via_dangling")]
        if not dang:
            break
        board = pcbnew.LoadBoard(PCB)
        for v in dang:
            pos = v["items"][0]["pos"]
            p = pcbnew.VECTOR2I(mm(pos["x"]), mm(pos["y"]))
            for t in list(board.GetTracks()):
                if t.Type() == pcbnew.PCB_VIA_T:
                    hit = abs(t.GetPosition().x - p.x) < mm(0.01) and abs(t.GetPosition().y - p.y) < mm(0.01)
                else:
                    hit = t.HitTest(p, 0)
                if hit and t.GetNetname() == v["items"][0]["description"].split("[")[1].split("]")[0]:
                    board.Delete(t)
                    trimmed += 1
                    break
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(PCB, board)
    print("patch: %d connections closed, %d dangling vias removed, %d stubs trimmed" % (fixed, removed, trimmed))


def fab(out_dir):
    """JLCPCB BOM/CPL from the routed board. Positions use the bottom-left aux origin."""
    import csv
    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    os.makedirs(out_dir, exist_ok=True)
    by_ref = {p["ref"]: p for p in D.parts}
    rows, groups = [], {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        p = by_ref.get(ref)
        if p is None:
            continue
        val, mpn, mfr, lcsc, lib, fpn, asm = D.PARTS[p["part"]]
        if asm == "NONE":
            continue
        # Placement centre = centre of the pad field (footprint origins of connectors sit on pin 1).
        bb = None
        for pad in fp.Pads():
            pb = pad.GetBoundingBox()
            if bb is None:
                bb = pb
            else:
                bb.Merge(pb)
        pos = bb.GetCenter() if bb is not None else fp.GetPosition()
        x = pcbnew.ToMM(pos.x) - OX
        y = D.BOARD_H - (pcbnew.ToMM(pos.y) - OY)
        rows.append((ref, x, y, fp.GetOrientationDegrees() % 360, asm, part_value(p), mpn, mfr, lcsc, fpn))
        groups.setdefault((val, mpn, lcsc, fpn, asm), []).append(ref)

    def refkey(r):
        i = 0
        while i < len(r) and not r[i].isdigit():
            i += 1
        return (r[:i], int(r[i:]) if r[i:].isdigit() else 0)

    with open(os.path.join(out_dir, "bom-jlcpcb.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "JLCPCB Part #"])
        for (val, mpn, lcsc, fpn, asm), refs in sorted(groups.items(), key=lambda kv: refkey(sorted(kv[1], key=refkey)[0])):
            w.writerow([mpn, ",".join(sorted(refs, key=refkey)), fpn, lcsc])
    with open(os.path.join(out_dir, "cpl-jlcpcb.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Rotation", "Layer"])
        for r in sorted(rows, key=lambda r: refkey(r[0])):
            w.writerow([r[0], "%.4f" % r[1], "%.4f" % r[2], "%.1f" % r[3], "Top"])
    with open(os.path.join(out_dir, "bom-engineering.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Value", "Manufacturer", "MPN", "Footprint", "JLCPCB Part #", "Assembly"])
        for r in sorted(rows, key=lambda r: refkey(r[0])):
            w.writerow([r[0], r[5], r[7], r[6], r[9], r[8], r[4]])
        w.writerow(["A1", "Teensy 4.1 with pins", "PJRC", "TEENSY41_PINS", "socketed in J2/J3", "", "Manual"])
    print("fab rows", len(rows), "groups", len(groups))


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "fab":
        fab(sys.argv[2])
        return
    if stage == "patch":
        patch()
        return
    if stage in ("sch", "all", "pcb"):
        used = write_symbol_lib()
        sym_uuid = write_schematic(used)
        write_project_files()
        if stage in ("pcb", "all"):
            build_pcb(sym_uuid)
    if stage in ("route", "all"):
        route(int(os.environ.get("PASSES", "40")))
    if stage in ("finish", "all"):
        finish()


if __name__ == "__main__":
    main()
