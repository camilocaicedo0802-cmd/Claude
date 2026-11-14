"""Flat icon badges drawn in code (no emoji): white glyph on a brand-orange disc with a white rim."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from gfx import FONTS, ORANGE, ORANGE_L

S = 480                     # supersampled badge size
C = S // 2
WH = (255, 255, 255, 255)
OR = ORANGE + (255,)


def _rot(pts, deg, c=(C, C)):
    a = math.radians(deg)
    return [(c[0] + (x - c[0]) * math.cos(a) - (y - c[1]) * math.sin(a),
             c[1] + (x - c[0]) * math.sin(a) + (y - c[1]) * math.cos(a)) for x, y in pts]


def _rrect(d, box, r, fill, deg=0, c=None):
    if deg == 0:
        d.rounded_rectangle(box, r, fill=fill)
        return
    x0, y0, x1, y1 = box
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    d.polygon(_rot(pts, deg, c or ((x0 + x1) / 2, (y0 + y1) / 2)), fill=fill)


def g_tag(d):
    pts = _rot([(120, 175), (290, 175), (385, 240), (290, 305), (120, 305)], -22)
    d.polygon(pts, fill=WH)
    hx, hy = _rot([(160, 240)], -22)[0]
    d.ellipse((hx - 18, hy - 18, hx + 18, hy + 18), fill=OR)
    f = ImageFont.truetype(FONTS + 'Poppins-Bold.ttf', 120)
    d.text((262, 248), '$', font=f, fill=OR, anchor='mm')


def g_spray(d):
    d.rounded_rectangle((185, 235), r := 0, fill=None) if False else None
    d.rounded_rectangle((190, 240, 300, 375), 26, fill=WH)
    d.rectangle((222, 196, 268, 244), fill=WH)
    d.polygon([(200, 150), (305, 150), (305, 200), (200, 200)], fill=WH)
    d.rectangle((305, 162, 340, 184), fill=WH)
    for x, y, r in [(366, 140, 11), (388, 172, 9), (370, 205, 10), (398, 112, 8), (402, 228, 7)]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=WH)
    d.rectangle((210, 290, 280, 302), fill=OR)


def g_factory(d):
    d.polygon([(130, 360), (130, 225), (190, 262), (190, 225), (250, 262), (250, 225), (310, 262), (310, 360)], fill=WH)
    d.rectangle((318, 150, 352, 360), fill=WH)
    for x in (152, 212, 272):
        d.rectangle((x, 295, x + 26, 325), fill=OR)


def g_swatches(d):
    piv = (240, 352)
    for deg, col in ((-32, (255, 226, 205, 255)), (0, (255, 244, 236, 255)), (32, WH)):
        pts = _rot([(198, 128), (282, 128), (282, 360), (198, 360)], deg, piv)
        d.polygon(pts, fill=col, outline=OR, width=9)
        band = _rot([(198, 128), (282, 128), (282, 175), (198, 175)], deg, piv)
        d.polygon(band, fill=(255, 150, 100, 255), outline=OR, width=9)
    d.ellipse((226, 322, 254, 350), fill=OR)


def g_shield(d):
    d.polygon([(240, 120), (350, 165), (340, 275), (240, 365), (140, 275), (130, 165)], fill=WH)
    d.line([(188, 245), (228, 287), (300, 200)], fill=OR, width=26, joint='curve')


def _bez(p0, p1, p2, p3, n=16):
    return [((1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0],
             (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1])
            for u in np.linspace(0, 1, n)]


def g_flame(d):
    out = (_bez((240, 368), (330, 368), (352, 290), (318, 232)) + _bez((318, 232), (298, 196), (284, 160), (268, 112)) +
           _bez((268, 112), (250, 160), (226, 175), (214, 196)) + _bez((214, 196), (200, 175), (196, 168), (196, 160)) +
           _bez((196, 160), (150, 215), (128, 260), (138, 305)) + _bez((138, 305), (150, 352), (195, 368), (240, 368)))
    d.polygon(out, fill=WH)
    inner = (_bez((240, 352), (288, 352), (300, 312), (282, 280)) + _bez((282, 280), (268, 256), (258, 236), (252, 210)) +
             _bez((252, 210), (230, 246), (206, 262), (198, 296)) + _bez((198, 296), (192, 330), (210, 352), (240, 352)))
    d.polygon(inner, fill=OR)


def g_pot(d):
    d.rounded_rectangle((150, 245, 330, 355), 30, fill=WH)
    d.rounded_rectangle((135, 222, 345, 244), 10, fill=WH)
    d.rounded_rectangle((222, 198, 258, 224), 8, fill=WH)
    d.rounded_rectangle((108, 262, 152, 282), 8, fill=WH)
    d.rounded_rectangle((328, 262, 372, 282), 8, fill=WH)
    for x in (190, 240, 290):
        pts = [(x + 12 * math.sin(i / 6 * math.pi * 1.5), 185 - i * 12) for i in range(7)]
        d.line(pts, fill=WH, width=12, joint='curve')


def g_warning(d):
    d.polygon([(240, 120), (370, 345), (110, 345)], fill=WH)
    d.rounded_rectangle((228, 190, 252, 282), 10, fill=OR)
    d.ellipse((227, 297, 253, 323), fill=OR)


def g_calendar(d):
    d.rounded_rectangle((140, 170, 340, 355), 26, fill=WH)
    d.rectangle((140, 205, 340, 222), fill=OR)
    for x in (188, 278):
        d.rounded_rectangle((x, 140, x + 18, 192), 9, fill=WH)
    for i, x in enumerate((172, 222, 272)):
        for j, y in enumerate((245, 295)):
            d.rounded_rectangle((x, y, x + 36, y + 32), 6, fill=OR)


def g_warehouse(d):
    d.polygon([(118, 225), (240, 140), (362, 225)], fill=WH)
    d.rectangle((145, 222, 335, 358), fill=WH)
    d.rectangle((190, 262, 290, 358), fill=OR)
    for y in (285, 310, 335):
        d.rectangle((190, y, 290, y + 7), fill=WH)


def g_worker(d):
    d.chord((168, 140, 312, 290), 180, 360, fill=WH)
    d.rounded_rectangle((145, 205, 335, 228), 10, fill=WH)
    d.rectangle((232, 140, 248, 200), fill=OR)
    d.ellipse((190, 232, 290, 322), fill=WH)
    d.chord((130, 320, 350, 520), 180, 360, fill=WH)


def g_kitchen(d):
    d.polygon([(205, 132), (275, 132), (322, 205), (158, 205)], fill=WH)
    d.rectangle((228, 112, 252, 134), fill=WH)
    d.rounded_rectangle((128, 238, 352, 258), 6, fill=WH)
    d.rectangle((140, 262, 340, 352), fill=WH)
    d.rectangle((236, 262, 244, 352), fill=OR)
    d.ellipse((212, 298, 226, 312), fill=OR); d.ellipse((254, 298, 268, 312), fill=OR)


GLYPHS = dict(tag=g_tag, spray=g_spray, factory=g_factory, swatches=g_swatches, shield=g_shield, flame=g_flame,
              pot=g_pot, warning=g_warning, calendar=g_calendar, warehouse=g_warehouse, worker=g_worker,
              kitchen=g_kitchen)


def badge(name, size=136):
    """PIL RGBA badge."""
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    # orange gradient disc
    yy = np.linspace(0, 1, S)[:, None]
    col = np.array(ORANGE_L, np.float32)[None, None] * (1 - yy[..., None]) + np.array(ORANGE, np.float32)[None, None] * yy[..., None]
    col = np.repeat(col, S, 1)
    m = Image.new('L', (S, S), 0)
    ImageDraw.Draw(m).ellipse((14, 14, S - 14, S - 14), fill=255)
    disc = Image.fromarray(np.dstack([col.astype(np.uint8), np.asarray(m)]), 'RGBA')
    ring = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((6, 6, S - 6, S - 6), fill=WH)
    im.alpha_composite(ring)
    im.alpha_composite(disc)
    # soft top highlight
    hl = Image.new('L', (S, S), 0)
    ImageDraw.Draw(hl).ellipse((70, 30, S - 70, S // 2), fill=60)
    hl = hl.filter(ImageFilter.GaussianBlur(30))
    im.alpha_composite(Image.merge('RGBA', [Image.new('L', (S, S), 255)] * 3 + [Image.fromarray(np.minimum(np.asarray(hl), np.asarray(m)))]))
    GLYPHS[name](ImageDraw.Draw(im))
    # keep everything inside the disc + ring
    outer = Image.new('L', (S, S), 0)
    ImageDraw.Draw(outer).ellipse((6, 6, S - 6, S - 6), fill=255)
    a = np.minimum(np.asarray(im)[..., 3], np.asarray(outer))
    im.putalpha(Image.fromarray(a))
    return im.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    row = Image.new('RGBA', (len(GLYPHS) * 150, 160), (60, 60, 60, 255))
    for i, n in enumerate(GLYPHS):
        row.alpha_composite(badge(n), (i * 150 + 7, 12))
    row.convert('RGB').save('/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel5/stills/icons.png')
