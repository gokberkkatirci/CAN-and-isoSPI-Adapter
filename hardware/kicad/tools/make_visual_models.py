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


def box(x, y, z, dx, dy, dz, color):
    """Positions and dimensions in millimetres. VRML KiCad units are 0.1 in."""
    pos = ' '.join(f'{v/2.54:.6f}' for v in (x,y,z))
    size = ' '.join(f'{v/2.54:.6f}' for v in (dx,dy,dz))
    rgb = ' '.join(str(v) for v in color)
    return (f'Transform {{ translation {pos} children [ Shape {{ '
            f'appearance Appearance {{ material Material {{ diffuseColor {rgb} }} }} '
            f'geometry Box {{ size {size} }} }} ] }}')


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


if __name__ == '__main__':
    DEST.mkdir(exist_ok=True)
    qfn()
    bourns()
    wurth()
    switch()
    nano()
