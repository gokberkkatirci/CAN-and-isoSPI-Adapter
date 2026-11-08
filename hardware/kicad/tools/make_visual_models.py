#!/usr/bin/env python3
"""Build compact VRML visualization models using package drawing dimensions."""
from pathlib import Path

DEST = Path(__file__).resolve().parents[1] / 'models'
TIN = (.72, .75, .77)
GOLD = (.86, .62, .23)
BLACK = (.085, .09, .10)
FERRITE = (.25, .26, .29)
GREEN = (.045, .29, .15)
TEAL = (.03, .44, .49)
WHITE = (.86, .86, .82)


METALS = {TIN, GOLD}


def material(color):
    """Glossy material for metal finishes, satin for plastics and solder mask."""
    rgb = ' '.join(str(v) for v in color)
    if color in METALS:
        return (f'material Material {{ diffuseColor {rgb} specularColor 0.9 0.9 0.85 '
                f'shininess 0.8 ambientIntensity 0.3 }}')
    return (f'material Material {{ diffuseColor {rgb} specularColor 0.25 0.25 0.25 '
            f'shininess 0.25 ambientIntensity 0.2 }}')


def box(x, y, z, dx, dy, dz, color):
    """Positions and dimensions in millimetres. VRML KiCad units are 0.1 in."""
    pos = ' '.join(f'{v/2.54:.6f}' for v in (x,y,z))
    size = ' '.join(f'{v/2.54:.6f}' for v in (dx,dy,dz))
    return (f'Transform {{ translation {pos} children [ Shape {{ '
            f'appearance Appearance {{ {material(color)} }} '
            f'geometry Box {{ size {size} }} }} ] }}')


def cyl(x, y, z, d, h, color):
    """Vertical cylinder centred at (x, y, z), diameter d, height h (mm)."""
    pos = ' '.join(f'{v/2.54:.6f}' for v in (x,y,z))
    return (f'Transform {{ translation {pos} rotation 1 0 0 1.5708 children [ Shape {{ '
            f'appearance Appearance {{ {material(color)} }} '
            f'geometry Cylinder {{ radius {d/2/2.54:.6f} height {h/2.54:.6f} }} }} ] }}')


def write(name, description, objects):
    (DEST / (name+'.wrl')).write_text(
        '#VRML V2.0 utf8\n# '+description+'\n'+'\n'.join(objects)+'\n')


def qfn():
    objects = [box(0,0,.418,5,5,.665,BLACK), box(0,0,.04,2.1,2.1,.08,TIN),
               box(-1.87,1.87,.753,.34,.34,.012,FERRITE)]
    for i in range(8):
        d = -1.75+.5*i
        for side in (-1,1):
            objects.append(box(side*2.28,d,.055,.44,.25,.11,TIN))
            objects.append(box(d,side*2.28,.055,.25,.44,.11,TIN))
    write('ADBMS6822_05-08-7057','ADI package 05-08-7057 visual approximation.',objects)


def bourns():
    objects = [box(0,0,.54,13.6,8.5,.74,BLACK),
               box(-4.3,0,1.15,5.0,8.32,.62,GREEN),box(4.3,0,1.15,5.0,8.32,.62,GREEN),
               box(0,0,2.76,8.05,8.25,3.32,FERRITE),
               box(0,0,4.71,8.3,8.3,1.38,FERRITE),
               box(-5.45,3.18,1.48,.62,.58,.08,WHITE)]
    for side in (-1,1):
        for y in (-2.54,0,2.54):
            objects += [box(side*6.35,y,.11,1.3,.5,.22,TIN),
                        box(side*6.06,y,.50,.29,.5,.78,TIN),
                        box(side*6.12,y,1.48,1.35,.5,.15,TIN)]
    write('SM91801AL-E','Bourns SM91801AL datasheet envelope and leads.',objects)


def wurth():
    objects = [box(0,0,.56,7.14,6.73,1.03,BLACK),
               box(0,0,2.4,7.05,6.65,3.35,FERRITE),
               box(0,0,4.105,6.7,6.4,.17,BLACK),
               box(-2.58,2.25,4.198,.45,.45,.018,WHITE)]
    for side in (-1,1):
        for y in (-2.54,0,2.54):
            objects += [box(side*4.45,y,.09,1.25,.65,.18,TIN),
                        box(side*3.9,y,.45,.26,.65,.73,TIN)]
    write('WE_760390014','Würth WE-PPTI 760390014 datasheet envelope and leads.',objects)


def switch():
    objects = [box(0,0,1.25,11.6,4.0,2.5,BLACK),
               box(0,0,3.95,11.55,3.98,2.9,TIN),
               box(-1.25,0,6.4,2.0,2.0,2.0,BLACK),
               box(0,-1.98,1.35,11.1,.12,2.7,TIN),
               box(0,1.98,1.35,11.1,.12,2.7,TIN)]
    for x in (-2.5,0,2.5):
        objects.append(box(x,0,-2.25,.6,.5,4.7,TIN))
    write('EG1218','E-Switch EG1218 drawing-based visual model.',objects)


def nano():
    # Model origin is the first pin in the left carrier socket.
    objects = [box(7.62,-17.78,10.6,17.78,43.18,1.6,TEAL),
               box(7.62,1.67,12.72,8.94,7.0,2.64,TIN),
               box(7.62,5.18,12.74,7.22,.08,1.59,BLACK),
               box(7.62,5.24,12.71,5.80,.10,.25,TIN),
               box(7.62,-21.4,11.91,7.0,7.0,1.0,BLACK),
               box(7.62,-7.5,11.91,3.9,3.0,1.0,TIN),
               box(7.62,-36.1,12.88,5.2,4.4,2.95,WHITE),
               box(4.3,-30.4,11.91,3.5,3.5,1.0,FERRITE),
               box(10.6,-31.1,11.86,3.0,2.9,.9,BLACK)]
    for x in (0,15.24):
        objects.append(box(x,-17.78,8.54,2.54,38.1,2.52,BLACK))
        for i in range(15):
            objects += [box(x,-2.54*i,8.90,.64,.64,6.3,GOLD),
                        box(x,-2.54*i,11.409,1.52,1.52,.025,GOLD)]
    for x,y in ((3.35,-3.2),(11.87,-3.1),(11.85,-8.8),(3.3,-14.7),(11.9,-15.4),
                (4.3,-25.8),(11.45,-26.7),(3.4,-34.1),(11.55,-34.0)):
        objects.append(box(x,y,11.71,1.65,.75,.62,FERRITE))
    write('Nano-R4-mounted','Arduino Nano R4 mechanical envelope with representative top components.',objects)


def teensy41():
    # Model origin is pin 1 (GND) of the GND/0..32 socket row; pins run along -Y,
    # the second row is at +15.24 mm X. The Teensy rests on its pin-header
    # spacers on top of 8.5 mm sockets, so the module underside is 11.0 mm up.
    PJRC = (.02, .40, .18)
    SILK = (.93, .93, .90)
    ORANGE = (.95, .45, .05)
    TAN = (.60, .48, .32)
    z0, t = 11.0, 1.6
    top = z0 + t
    objects = [box(7.62, -29.21, z0 + t / 2, 17.78, 60.96, t, PJRC)]
    # micro-USB receptacle overhanging the USB end
    objects += [box(7.62, 1.2, top + 1.3, 7.6, 5.6, 2.6, TIN), box(7.62, 3.9, top + 1.3, 6.6, .3, 1.6, BLACK)]
    # i.MX RT1062 BGA, QSPI flash (SOIC-8), Ethernet PHY, buck and crystals
    objects += [box(7.62, -27.0, top + .6, 10.0, 10.0, 1.2, BLACK), box(7.62, -27.0, top + 1.21, 9.0, 9.0, .02, FERRITE)]
    objects += [box(7.62, -13.5, top + .7, 5.0, 4.0, 1.4, BLACK)]
    for k in range(4):
        for side in (-1, 1):
            objects.append(box(7.62 + side * 3.0, -13.5 - 1.905 + k * 1.27, top + .3, 1.0, .4, .2, TIN))
    objects += [box(11.6, -37.5, top + .45, 3.0, 3.0, .9, BLACK), box(3.0, -36.0, top + .45, 2.5, 2.5, .9, BLACK),
                box(12.6, -20.5, top + .4, 3.2, 2.5, .8, TIN), box(3.2, -21.0, top + .35, 2.0, 1.6, .7, TIN)]
    # microSD socket at the far end
    objects += [box(7.62, -53.4, top + .75, 11.5, 12.0, 1.5, TIN), box(7.62, -59.2, top + .75, 10.0, .4, .9, BLACK)]
    # program button, power LED and a scatter of 0402 passives
    objects += [box(3.4, -6.5, top + .25, 3.4, 2.6, .5, BLACK), box(3.4, -6.5, top + .8, 2.0, 1.4, .6, SILK),
                box(12.4, -6.0, top + .25, 1.0, .5, .5, ORANGE)]
    for k, (x, y) in enumerate(((2.5, -10.0), (12.8, -10.5), (2.4, -16.0), (12.8, -15.8), (2.6, -30.5), (12.7, -31.0),
                                (2.5, -33.0), (12.6, -33.4), (4.5, -40.5), (10.8, -41.0), (2.8, -44.0), (12.5, -44.5),
                                (6.0, -19.0), (9.5, -19.2), (5.5, -34.5), (9.8, -34.8))):
        objects.append(box(x, y, top + .2, 1.0, .5, .4, TAN if k % 3 else BLACK))
    # header pins: plastic spacer under the board, gold pins, plated pads on top
    for x in (0, 15.24):
        objects.append(box(x, -29.21, 9.75, 2.54, 60.96, 2.5, BLACK))
        for i in range(24):
            objects += [cyl(x, -2.54 * i, 8.6, .64, 6.6, GOLD),
                        cyl(x, -2.54 * i, top + .03, 1.6, .06, GOLD),
                        cyl(x, -2.54 * i, top + .45, .64, .8, TIN)]
    # USB host header holes and silkscreen frame
    for k in range(5):
        objects.append(cyl(4.69, -6.3 - 2.54 * k, top + .03, 1.4, .06, GOLD))
    objects += [box(.9, -29.21, top + .01, .15, 58.0, .02, SILK), box(14.34, -29.21, top + .01, .15, 58.0, .02, SILK)]
    write('Teensy41-mounted', 'Teensy 4.1 with representative top components, resting on 8.5 mm sockets.', objects)


def pogo():
    objects = [cyl(0, 0, .05, 1.9, .1, TIN),
               cyl(0, 0, 4.0, 2.0, 7.8, GOLD),
               cyl(0, 0, 8.05, 2.3, .3, GOLD),
               cyl(0, 0, 9.6, 1.0, 3.2, GOLD)]
    write('Pogo_YTC1P-8535', 'YIYUAN YTC1P-8535-01 pogo pin, 2 mm barrel, 12 mm free length.', objects)


def usbc():
    # HRO TYPE-C-31-M-12 envelope on the KiCad footprint origin; the opening faces -Y in model space.
    objects = [box(0, -0.35, 1.63, 8.94, 7.35, 3.26, TIN),
               box(0, -4.0, 1.63, 6.9, .1, 2.2, BLACK),
               box(0, -3.0, 1.63, 5.6, 2.0, .6, BLACK)]
    for x in (-3.25, -2.45, -1.75, -1.25, -.75, -.25, .25, .75, 1.25, 1.75, 2.45, 3.25):
        objects.append(box(x, 4.0, .05, .25, 1.0, .1, TIN))
    for x in (-4.32, 4.32):
        objects += [box(x, 3.13, .8, .6, 1.6, 1.6, TIN), box(x, -1.05, .8, .6, 1.2, 1.6, TIN)]
    write('USB_C_HRO_TYPE-C-31-M-12', 'HRO TYPE-C-31-M-12 USB-C receptacle envelope.', objects)


if __name__ == '__main__':
    DEST.mkdir(exist_ok=True)
    qfn()
    bourns()
    wurth()
    switch()
    nano()
    teensy41()
    pogo()
    usbc()
