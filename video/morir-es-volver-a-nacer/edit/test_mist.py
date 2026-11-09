import numpy as np, cv2, sys
from engine import W,H, texture
from mist import *
tiles=[]
def snap(base, ovs, t, dur=4.0, post=None):
    base.setup(dur); fr=base.frame(t).copy()
    for o in ovs: o.draw(fr,t,dur)
    if post: fr=post(fr,t,dur)
    fr=texture().apply(fr, int(t*30), grain=6, vignette=1.0)
    tiles.append(cv2.resize(fr,(640,360)))
snap(Embers(), [TypeLine("El 21 de julio de 1798... imagina que acabas de morir.", t0=0.1, y=0.15, size=40)], 2.0)
snap(Embers(), [Kinetic([[("¿Y SI MORIR",'w')],[("ES VOLVER A",'w'),("nacer?",'s')]], t0=0, size=150)], 3.0)
snap(LightTunnel(), [Kinetic([[("UNA LUZ",'w')],[("al final del túnel",'sy')]], t0=0, size=130, y=0.75)], 2.0)
snap(Corridor(), [NeonBox("Y ESO NO CUADRA", t0=0.0)], 2.0)
snap(Embers(color=(30,30,30)), [Rings(t0=0), BigNumber("500"," AÑOS ANTES",t0=0, count=(0,500,1.0), fmt="{:.0f}")], 2.0)
snap(Embers(), [Bar("9 MESES", ("OSCURIDAD","CALOR","SILENCIO"), t0=0), LowerName("TU PRIMER UNIVERSO", t0=0)], 3.0)
snap(Embers(), [Quote(["\"Cierras los ojos en una vida", "y los abres en otra.\""], t0=0, pos=(0.5,0.5))], 3.0, post=chroma(4))
snap(LightTunnel(intensity=(1,1)), [Kinetic([[("¿Y SI ESA LUZ",'w')],[("NO ES EL",'w'),("CIELO?",'r')]], t0=0, size=140, dim=0.3)], 2.0)
snap(Embers(), [Kinetic([[("Tal vez",'k')],[("HAS SIDO",'w'),("CIENTOS",'y')],[("de personas",'s')]], t0=0, size=140)], 3.0)
rows=[np.hstack(tiles[i:i+3]) for i in range(0,9,3)]
cv2.imwrite('/home/user/proj/ep/work/test_mist.jpg', cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
