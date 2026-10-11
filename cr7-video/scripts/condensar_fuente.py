# Genera TinosCondensed-BoldItalic.ttf: Tinos Bold Italic escalada horizontalmente al 70 % (estilo.md §3.1)
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
src, dst, sx = sys.argv[1], sys.argv[2], float(sys.argv[3])
f = TTFont(src)
glyf, hmtx = f["glyf"], f["hmtx"]
gs = f.getGlyphSet()
new = {}
for name in f.getGlyphOrder():
    # Se descomponen los glifos compuestos (É = E + ´) para no escalarlos dos veces
    rec = DecomposingRecordingPen(gs)
    gs[name].draw(rec)
    pen = TTGlyphPen(None)
    rec.replay(TransformPen(pen, (sx, 0, 0, 1, 0, 0)))
    new[name] = pen.glyph()
for name, g in new.items():
    glyf[name] = g
    adv, lsb = hmtx[name]
    hmtx[name] = (round(adv * sx), round(lsb * sx))
for t in ["GPOS", "kern", "hdmx", "LTSH", "VDMX"]:
    if t in f: del f[t]
for rec in f["name"].names:
    if rec.nameID in (1, 4, 6, 16):
        try:
            s = rec.toUnicode()
            rec.string = s.replace("Tinos", "Tinos Condensed").replace("Tinos-", "TinosCondensed-")
        except Exception: pass
f.save(dst); print("ok", dst)
