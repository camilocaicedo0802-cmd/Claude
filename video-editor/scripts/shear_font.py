"""Crea un estilo recto a partir de una cursiva oblicua (o al revés) aplicando un
cizallamiento a los contornos CFF. Mantiene anchos de avance, kerning y métricas.
Uso: python3 -I shear_font.py <entrada.otf> <salida.otf> <grados> <nombre_familia> <nombre_estilo>
  grados > 0 inclina a la derecha (crea cursiva); grados < 0 endereza una cursiva."""
import math
import sys

from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

src, dst, deg, family, style = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
k = math.tan(math.radians(deg))
font = TTFont(src)
gs = font.getGlyphSet()
cff = font["CFF "].cff
top = cff[cff.fontNames[0]]
cs = top.CharStrings
hmtx = font["hmtx"].metrics
for name in font.getGlyphOrder():
    width = hmtx[name][0]
    pen = T2CharStringPen(width, gs)
    gs[name].draw(TransformPen(pen, (1, 0, k, 1, 0, 0)))
    new = pen.getCharString(private=cs[name].private, globalSubrs=cs[name].globalSubrs)
    cs[name] = new
# métricas e indicadores de estilo
font["post"].italicAngle = -deg if deg > 0 else 0.0
os2 = font["OS/2"]
head = font["head"]
if deg > 0:
    os2.fsSelection = (os2.fsSelection | 1) & ~(1 << 6)
    head.macStyle |= 2
else:
    os2.fsSelection = (os2.fsSelection & ~1)
    head.macStyle &= ~2
top.ItalicAngle = font["post"].italicAngle
full = f"{family} {style}"
ps = (family + "-" + style).replace(" ", "")
for rec in font["name"].names:
    if rec.nameID in (1, 16):
        rec.string = family
    elif rec.nameID in (2, 17):
        rec.string = style
    elif rec.nameID == 4:
        rec.string = full
    elif rec.nameID == 6:
        rec.string = ps
cff.fontNames = [ps]
top.FullName = full
top.FamilyName = family
font.save(dst)
print("ok", dst)
