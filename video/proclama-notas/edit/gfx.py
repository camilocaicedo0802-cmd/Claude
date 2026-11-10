"""Gráficos y capas de marca (estilo Proclama del Pacífico) para las notas verticales."""
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from lib import (ASSETS, FPS, H, NAVY, RED, ROOT, W, WHITE, Seq, TextBlock, blend, censor, clamp, ease_back,
                 ease_in, ease_io, ease_out, font, layout, tokenize, vgrad, word_sprite)

GRAY = (150, 150, 155)


def rgba_canvas(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


# --------------------------------------------------------------------------------------- capas de marca
class Gradients:
    """Oscurece arriba (logo) y abajo (textos) para que todo se lea sobre cualquier imagen."""

    def __init__(self, t0, t1, top=0.45, bottom=0.82, bottom_from=1000):
        self.t0, self.t1 = t0, t1
        self.top = vgrad(0, 620, top, 0.0)
        self.bot = vgrad(bottom_from, H, 0.0, bottom)
        self.bf = bottom_from

    def draw(self, frame, t):
        if self.t0 <= t <= self.t1:
            blend(frame, self.top, 0, 0)
            blend(frame, self.bot, 0, self.bf)


class LogoBug:
    """Logo animado de Proclama (Logo_Vertical_2026.mov) arriba a la derecha."""

    def __init__(self, t0, t1, pulses=()):
        self.seq = Seq(ASSETS + '/logo')
        self.t0, self.t1, self.pulses = t0, t1, list(pulses)

    def draw(self, frame, t):
        if t < self.t0 or t > self.t1:
            return
        k = int((t - self.t0) * FPS)
        if k < 110:
            idx = k
        else:
            idx = 110
            for p in self.pulses:
                j = int((t - p) * FPS)
                if 0 <= j < 110:
                    idx = 567 + j
        j = int((self.t1 - t) * FPS)
        if j < 9:
            idx = 1144 - j
        blend(frame, self.seq.get(idx), 780, 320)


class Credit:
    """Crédito pequeño de la fuente del video (arriba a la izquierda)."""

    def __init__(self, text, t0, t1):
        fnt = font('Poppins-Medium', 25)
        spr, pad = word_sprite(text, fnt, WHITE, 'n', shadow=0.8)
        self.spr, self.pad, self.t0, self.t1 = spr, pad, t0, t1

    def draw(self, frame, t):
        if self.t0 <= t <= self.t1:
            a = clamp((t - self.t0) / 0.3) * clamp((self.t1 - t) / 0.3)
            frame_bar = np.zeros((30, 6, 4), np.uint8)
            frame_bar[:, :] = RED + (255,)
            blend(frame, frame_bar, 56, 404, a)
            blend(frame, self.spr, 72 - self.pad, 400 - self.pad, a)


class TitleCard:
    """Titular estilo reel de Proclama: Roboto Black en mayúsculas, palabras clave en caja roja,
    franja roja a la izquierda y la web debajo."""

    def __init__(self, lines, t0, t1, bottom=1470, size=72, line_h=76, url=True, x=130, out=0.3):
        self.fnt = font('Roboto-Black', size)
        self.t0, self.t1, self.out = t0, t1, out
        self.lines = []
        n = len(lines)
        top = bottom - n * line_h
        self.top, self.bottom, self.x = top, bottom, x
        for i, ln in enumerate(lines):
            items, _, _ = layout(ln, self.fnt, 2000, line_h)
            box_layer, text_layer = rgba_canvas(1000, line_h + 40), rgba_canvas(1000, line_h + 40)
            db, dt = ImageDraw.Draw(box_layer), ImageDraw.Draw(text_layer)
            asc, desc = self.fnt.getmetrics()
            ty = 20 + (line_h - asc - desc) // 2 + 4
            for (wx, wy, word, st, ww, li) in items:
                tx = 22 + wx
                if st == 'box':
                    db.rectangle([tx - 0, ty + int(asc * 0.16) - 8, tx + ww, ty + asc + 6], fill=RED + (255,))
                    tx += 14
                dt.text((tx, ty), word, font=self.fnt, fill=WHITE + (255,))
            sh = rgba_canvas(1000, line_h + 40)
            ImageDraw.Draw(sh).bitmap((0, 0), text_layer.split()[3], fill=(0, 0, 0, 150))
            sh = sh.filter(ImageFilter.GaussianBlur(6))
            self.lines.append((np.array(box_layer), np.array(Image.alpha_composite(sh, text_layer)), top + i * line_h - 20))
        self.url = None
        if url:
            spr, pad = word_sprite('www.proclamadelpacifico.com', font('Poppins-Regular', 30), WHITE, 'n', 0.7)
            self.url = (spr, (W - spr.shape[1]) // 2, 1548 - pad)

    def draw(self, frame, t):
        if t < self.t0 or t > self.t1:
            return
        ao = 1 - ease_in((t - (self.t1 - self.out)) / self.out)
        u = ease_out((t - self.t0) / 0.35)
        hh = int((self.bottom - self.top + 6) * u)
        if hh > 0:
            bar = np.zeros((hh, 10, 4), np.uint8)
            bar[:, :] = RED + (255,)
            blend(frame, bar, 57, self.top - 3, ao)
        for i, (box, txt, y) in enumerate(self.lines):
            s = self.t0 + 0.12 + i * 0.13
            e = ease_out((t - s) / 0.4)
            if e <= 0:
                continue
            x = self.x - 22 - 50 * (1 - e)
            wb = ease_out((t - s - 0.12) / 0.35)
            if wb > 0:
                cut = box.copy()
                cut[:, int(cut.shape[1] * wb):, 3] = 0
                blend(frame, cut, x, y, ao)
            blend(frame, txt, x, y, clamp(e * 1.4) * ao)
        if self.url:
            spr, x, y = self.url
            blend(frame, spr, x, y, clamp((t - self.t0 - 0.6) / 0.4) * ao)


class Transition:
    """Cortinilla de Proclama (PNG RGBA 1080x1920) a partir de t0."""

    def __init__(self, folder, t0):
        self.seq = Seq(ASSETS + '/' + folder)
        self.t0 = t0
        self.dur = len(self.seq) / FPS

    def draw(self, frame, t):
        k = int(round((t - self.t0) * FPS))
        if 0 <= k < len(self.seq):
            blend(frame, self.seq.get(k), 0, 0)


class Bajada(TextBlock):
    """Texto del guion en la parte baja (Poppins), palabra por palabra."""

    def __init__(self, text, t0, t1, bottom=1462, size=50, line_h=68, align='center', **kw):
        super().__init__(text, font('Poppins-SemiBold', size), 70, bottom, W - 140, line_h, t0, t1, align=align,
                         anchor='bottom', **kw)


# --------------------------------------------------------------------------------------- gráficos de datos
def fmt_num(v, thousands=True):
    s = f'{int(round(v)):,}'.replace(',', '.') if thousands else str(int(round(v)))
    return s


class Counters:
    """Dos (o uno) cifras grandes que cuentan hacia arriba con su etiqueta en caja roja."""

    def __init__(self, items, t0, t1, y=640, header=None, footer=None, size=250, cx=None):
        self.items, self.t0, self.t1, self.y, self.size = items, t0, t1, y, size
        self.fnt = font('Roboto-Black', size)
        self.lab = font('Roboto-Black', 50)
        self.header = TextBlock(header, font('Roboto-Black', 44), 70, y - 112, W - 140, 58, t0, t1, align='center',
                                stagger=0.03) if header else None
        self.footer = TextBlock(footer, font('Poppins-Regular', 28), 70, y + size + 250, W - 140, 40, t0 + 0.8, t1,
                                align='center', stagger=0.01, shadow=0.8) if footer else None
        n = len(items)
        self.cx = cx or ([W / 2] if n == 1 else [W * 0.27, W * 0.71])
        self.labels = []
        for k, it in enumerate(items):
            lines = it['label'].split('\\n')
            sprs = []
            for li, ln in enumerate(lines):
                spr, pad = word_sprite(censor_line(ln), self.lab, WHITE, 'box', line_h=62)
                sprs.append((spr, pad))
            self.labels.append(sprs)

    def draw(self, frame, t):
        if t < self.t0 or t > self.t1:
            return
        ao = 1 - ease_in((t - (self.t1 - 0.25)) / 0.25)
        if self.header:
            self.header.draw(frame, t)
        for k, it in enumerate(self.items):
            s = self.t0 + 0.15 + k * 0.45
            u = (t - s) / it.get('count', 1.3)
            if u <= 0:
                continue
            v = it['value'] * ease_out(u)
            txt = it.get('prefix', '') + fmt_num(v)
            CW = 700
            im = rgba_canvas(CW, self.size + 60)
            d = ImageDraw.Draw(im)
            tw = d.textlength(txt, font=self.fnt)
            sh = rgba_canvas(CW, self.size + 60)
            ImageDraw.Draw(sh).text(((CW - tw) / 2 + 4, 10), txt, font=self.fnt, fill=(0, 0, 0, 160))
            im = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), im)
            ImageDraw.Draw(im).text(((CW - tw) / 2, 4), txt, font=self.fnt, fill=it.get('color', WHITE) + (255,))
            sc = 0.85 + 0.15 * ease_back(clamp(u * 2.2))
            arr = np.array(im)
            if sc < 0.999:
                import cv2
                arr = cv2.resize(arr, (int(CW * sc), int((self.size + 60) * sc)), interpolation=cv2.INTER_AREA)
            blend(frame, arr, self.cx[k] - arr.shape[1] / 2, self.y + (self.size + 60) * (1 - sc) / 2,
                  clamp(u * 3) * ao)
            for li, (spr, pad) in enumerate(self.labels[k]):
                e = ease_out((t - s - 0.5 - li * 0.12) / 0.35)
                if e > 0:
                    cut = spr.copy()
                    cut[:, int(cut.shape[1] * e):, 3] = 0
                    blend(frame, cut, self.cx[k] - spr.shape[1] / 2, self.y + self.size + 10 + li * 72 - pad, ao)
        if self.footer:
            self.footer.draw(frame, t)


def censor_line(s):
    return ' '.join(censor(w) for w in s.split())


class RaceChart:
    """Acumulado mensual de 2026 frente a los totales anuales de 2021 y 2022 (datos Indepaz)."""

    MONTHS = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT']
    MONTHLY = [14, 9, 14, 13, 10, 9, 9, 9, 7, 3]

    def __init__(self, t0, t1, draw_dur=6.0, x0=150, x1=960, y0=790, y1=1110):
        self.t0, self.t1, self.dd = t0, t1, draw_dur
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.cum = list(np.cumsum(self.MONTHLY))
        self.vmax = 110
        # puntos: fin de cada mes; el último es el corte del 9 de octubre
        xs = [x0 + (x1 - x0) * (i + 1) / 10.0 for i in range(9)] + [x0 + (x1 - x0) * (9 + 9 / 31) / 10.0]
        self.pts = [(x0, self.yv(0))] + [(x, self.yv(v)) for x, v in zip(xs, self.cum)]
        self.vals = [0] + self.cum
        self.title = TextBlock(censor_line('M*SACRES ACUMULADAS EN 2026').replace('M*SACRES', '[M*SACRES]'),
                               font('Roboto-Black', 48), 70, y0 - 185, W - 140, 62, t0, t1, align='center', stagger=0.04)
        self.sub = TextBlock('Frente al total de todo 2021 y todo 2022', font('Poppins-Regular', 30), 70, y0 - 118,
                             W - 140, 40, t0 + 0.3, t1, align='center', stagger=0.02, shadow=0.8)
        self.foot = TextBlock('Fuente: Indepaz · Corte: 9 de octubre de 2026', font('Poppins-Regular', 26), 70,
                              y1 + 52, W - 140, 36, t0 + 0.6, t1, align='center', stagger=0.01, shadow=0.8)
        self.static = self._static()

    def yv(self, v):
        return self.y1 - (self.y1 - self.y0) * v / self.vmax

    def _static(self):
        im = rgba_canvas(W, H)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([60, self.y0 - 205, W - 60, self.y1 + 100], 28, fill=(10, 10, 12, 170))
        for v in (0, 25, 50, 75, 100):
            y = self.yv(v)
            d.line([self.x0, y, self.x1, y], fill=(255, 255, 255, 40), width=2)
            d.text((self.x0 - 18, y), str(v), font=font('Poppins-Regular', 24), fill=(200, 200, 200, 255), anchor='rm')
        for i, m in enumerate(self.MONTHS):
            x = self.x0 + (self.x1 - self.x0) * (i + 0.5) / 10
            d.text((x, self.y1 + 22), m, font=font('Poppins-Medium', 22), fill=(210, 210, 210, 255), anchor='mm')
        return np.array(im)

    def _refline(self, d, v, label, color, above, alpha):
        y = self.yv(v)
        x = self.x0
        while x < self.x1:
            d.line([x, y, min(x + 16, self.x1), y], fill=color + (int(255 * alpha),), width=4)
            x += 26
        f = font('Roboto-Black', 30)
        ty = y - 24 if above else y + 24
        d.text((self.x0 + 8, ty), label, font=f, fill=color + (int(255 * alpha),), anchor='lm')

    def draw(self, frame, t):
        if t < self.t0 or t > self.t1:
            return
        ao = 1 - ease_in((t - (self.t1 - 0.3)) / 0.3)
        a = clamp((t - self.t0) / 0.4) * ao
        blend(frame, self.static, 0, 0, a)
        self.title.draw(frame, t)
        self.sub.draw(frame, t)
        self.foot.draw(frame, t)
        im = rgba_canvas(W, H)
        d = ImageDraw.Draw(im)
        ra = clamp((t - self.t0 - 0.5) / 0.5)
        self._refline(d, 96, 'TODO 2021: 96', (235, 235, 235), True, ra)
        self._refline(d, 94, 'TODO 2022: 94', (160, 160, 165), False, ra)
        # línea 2026
        u = ease_io((t - self.t0 - 1.0) / self.dd)
        if u > 0:
            n = len(self.pts) - 1
            pos = u * n
            k = int(pos)
            fr = pos - k
            pts = self.pts[:k + 1]
            if k < n:
                (xa, ya), (xb, yb) = self.pts[k], self.pts[k + 1]
                pts = pts + [(xa + (xb - xa) * fr, ya + (yb - ya) * fr)]
                val = self.vals[k] + (self.vals[k + 1] - self.vals[k]) * fr
            else:
                val = self.vals[-1]
            poly = pts + [(pts[-1][0], self.y1), (self.x0, self.y1)]
            d.polygon(poly, fill=RED + (70,))
            d.line(pts, fill=RED + (255,), width=9, joint='curve')
            hx, hy = pts[-1]
            d.ellipse([hx - 13, hy - 13, hx + 13, hy + 13], fill=WHITE + (255,), outline=RED + (255,), width=6)
            lab = f'2026: {int(round(val))}'
            f = font('Roboto-Black', 40)
            tw = d.textlength(lab, font=f)
            bx = min(hx - tw / 2 - 14, self.x1 - tw - 28)
            by = hy - 78
            d.rectangle([bx, by, bx + tw + 28, by + 54], fill=RED + (255,))
            d.text((bx + 14, by + 27), lab, font=f, fill=WHITE + (255,), anchor='lm')
            if u >= 1:
                e = ease_back(clamp((t - self.t0 - 1.0 - self.dd - 0.2) / 0.45))
                if e > 0:
                    badge = censor_line('RÉCORD DESDE 2016')
                    fb = font('Roboto-Black', int(34 * e) + 1)
                    tw2 = d.textlength(badge, font=fb)
                    d.rectangle([hx - tw2 - 60, hy + 34, hx - 32, hy + 90], fill=WHITE + (255,))
                    d.text((hx - tw2 / 2 - 46, hy + 62), badge, font=fb, fill=RED + (255,), anchor='mm')
        blend(frame, np.array(im), 0, 0, ao)


class MapCO:
    """Mapa de Colombia por departamentos (Natural Earth, dominio público) con Cauca y Antioquia resaltados."""

    def __init__(self, t0, t1, t_cauca_label, t_antioquia, box=(170, 575, 1000, 1170)):
        self.t0, self.t1, self.tcl, self.ta = t0, t1, t_cauca_label, t_antioquia
        gj = json.load(open(ROOT + '/work/map/col_adm1.geojson'))
        self.deps = {}
        allpts = []
        for f in gj['features']:
            name = f['properties'].get('name') or 'Bogotá'
            g = f['geometry']
            polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            rings = []
            for p in polys:
                ring = p[0]
                if min(x for x, y in ring) < -80:  # San Andrés y Providencia
                    continue
                rings.append(ring)
                allpts += ring
            self.deps[name] = rings
        xs = [p[0] for p in allpts]
        ys = [p[1] for p in allpts]
        lon0, lon1, lat0, lat1 = min(xs), max(xs), min(ys), max(ys)
        k = math.cos(math.radians((lat0 + lat1) / 2))
        bx0, by0, bx1, by1 = box
        sc = min((bx1 - bx0) / ((lon1 - lon0) * k), (by1 - by0) / (lat1 - lat0))
        ox = bx0 + ((bx1 - bx0) - (lon1 - lon0) * k * sc) / 2
        oy = by0 + ((by1 - by0) - (lat1 - lat0) * sc) / 2
        self.proj = lambda lon, lat: (ox + (lon - lon0) * k * sc, oy + (lat1 - lat) * sc)
        self.scr = {n: [[self.proj(x, y) for x, y in r] for r in rings] for n, rings in self.deps.items()}
        self.base = self._base()
        self.cent = {n: self._centroid(n) for n in ('Cauca', 'Antioquia')}
        self.title = TextBlock('[EL CAUCA] ENTRE LOS \\n TERRITORIOS MÁS AFECTADOS', font('Roboto-Black', 46), 70, 420, 740,
                               62, t0, t1, align='left', stagger=0.04)
        self.foot = TextBlock('Fuente: Indepaz · 1 de enero al 9 de octubre de 2026', font('Poppins-Regular', 26), 70,
                              1186, W - 140, 36, t0 + 0.5, t1, align='center', stagger=0.01, shadow=0.8)

    def _centroid(self, n):
        pts = max(self.scr[n], key=len)
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    def _base(self):
        im = rgba_canvas(W, H)
        d = ImageDraw.Draw(im)
        for n, rings in self.scr.items():
            for r in rings:
                d.polygon(r, fill=(58, 58, 64, 255), outline=(120, 120, 130, 255))
        glow = im.filter(ImageFilter.GaussianBlur(14))
        g = np.array(glow)
        g[:, :, :3] = (0, 0, 0)
        g[:, :, 3] = (g[:, :, 3] * 0.6).astype(np.uint8)
        out = Image.alpha_composite(Image.fromarray(g), im)
        return np.array(out)

    def draw(self, frame, t):
        if t < self.t0 or t > self.t1:
            return
        ao = 1 - ease_in((t - (self.t1 - 0.3)) / 0.3)
        e = ease_out((t - self.t0) / 0.6)
        blend(frame, self.base, 0, 30 * (1 - e), e * ao)
        self.title.draw(frame, t)
        self.foot.draw(frame, t)
        im = rgba_canvas(W, H)
        d = ImageDraw.Draw(im)
        # Cauca: se llena y late
        uc = clamp((t - self.t0 - 0.6) / 0.5)
        if uc > 0:
            pulse = 0.82 + 0.18 * math.sin((t - self.t0) * 4.2)
            for r in self.scr['Cauca']:
                d.polygon(r, fill=RED + (int(255 * uc * pulse),), outline=WHITE + (int(255 * uc),))
        ua = clamp((t - self.ta) / 0.5)
        if ua > 0:
            for r in self.scr['Antioquia']:
                d.polygon(r, fill=(236, 110, 110, int(235 * ua)), outline=WHITE + (int(255 * ua),))
        blend(frame, np.array(im), 0, 30 * (1 - e), ao)
        # etiquetas
        self._callout(frame, t, self.tcl, self.cent['Cauca'], 'CAUCA',
                      [censor_line('14 m*sacres'), 'al menos 68 víctimas'], (70, 960), ao)
        self._callout(frame, t, self.ta + 0.3, self.cent['Antioquia'], 'ANTIOQUIA',
                      ['alta concentración'], (70, 640), ao)

    def _callout(self, frame, t, ts, anchor, head, lines, pos, ao):
        u = ease_out((t - ts) / 0.45)
        if u <= 0:
            return
        im = rgba_canvas(W, H)
        d = ImageDraw.Draw(im)
        fh, fl = font('Roboto-Black', 44), font('Poppins-SemiBold', 34)
        bw = max(d.textlength(head, font=fh), *[d.textlength(s, font=fl) for s in lines]) + 44
        bh = 64 + 46 * len(lines)
        x, y = pos
        ax, ay = anchor
        d.line([x + bw, y + bh / 2, ax, ay], fill=WHITE + (230,), width=3)
        d.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], fill=WHITE + (255,))
        d.rectangle([x, y, x + bw, y + bh], fill=(12, 12, 14, 225))
        d.rectangle([x, y, x + 8, y + bh], fill=RED + (255,))
        d.text((x + 24, y + 12), head, font=fh, fill=WHITE + (255,))
        for i, s in enumerate(lines):
            d.text((x + 24, y + 62 + i * 46), s, font=fl, fill=(255, 210, 210, 255) if i == 0 else (230, 230, 230, 255))
        arr = np.array(im)
        arr[:, :int(x + (bw + 40) * u) + 1][:, :, 3] = arr[:, :int(x + (bw + 40) * u) + 1][:, :, 3]
        if u < 1:
            arr[:, int(x + (bw + 40) * u):, 3] = 0
        blend(frame, arr, 0, 0, ao)


class ListCards:
    """Lista numerada que va apareciendo (factores del aumento)."""

    def __init__(self, items, times, t1, y=560, gap=26):
        self.t1 = t1
        self.cards = []
        fnt = font('Poppins-SemiBold', 42)
        fn = font('Roboto-Black', 64)
        cy = y
        for i, (txt, t0) in enumerate(zip(items, times)):
            lay, hgt, nl = layout(txt, fnt, 760, 56)
            ch = max(130, hgt + 44)
            im = rgba_canvas(W - 120, ch)
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, W - 121, ch - 1], 18, fill=(10, 10, 12, 205))
            d.rectangle([0, 0, 118, ch - 1], fill=RED + (255,))
            d.text((59, ch / 2), str(i + 1), font=fn, fill=WHITE + (255,), anchor='mm')
            for (wx, wy, word, st, ww, li) in lay:
                d.text((150 + wx, 22 + wy), word, font=fnt, fill=WHITE + (255,))
            self.cards.append((np.array(im), cy, t0))
            cy += ch + gap

    def draw(self, frame, t):
        if t > self.t1:
            return
        ao = 1 - ease_in((t - (self.t1 - 0.3)) / 0.3)
        for spr, y, t0 in self.cards:
            u = ease_out((t - t0) / 0.45)
            if u > 0:
                blend(frame, spr, 60 - 80 * (1 - u), y, clamp(u * 1.5) * ao)


class Question:
    """Pregunta final al público + invitación a comentar."""

    def __init__(self, lines, t0, t1, cta='Déjanos tu opinión en los comentarios'):
        self.title = TitleCard(lines, t0, t1, bottom=1200, size=66, line_h=72, url=False)
        self.cta = TextBlock(cta, font('Poppins-Medium', 38), 70, 1268, W - 140, 50, t0 + 1.2, t1, align='center',
                             stagger=0.04, shadow=0.8)
        self.t0, self.t1 = t0, t1

    def draw(self, frame, t):
        self.title.draw(frame, t)
        self.cta.draw(frame, t)
        if self.t0 + 1.2 <= t <= self.t1:
            u = ease_back(clamp((t - self.t0 - 1.2) / 0.4))
            im = rgba_canvas(120, 120)
            d = ImageDraw.Draw(im)
            r = 34 * u
            d.ellipse([60 - r, 50 - r * 0.8, 60 + r, 50 + r * 0.8], fill=RED + (255,))
            d.polygon([(45, 50 + r * 0.6), (38, 50 + r * 1.25), (62, 50 + r * 0.7)], fill=RED + (255,))
            for k in (-1, 0, 1):
                d.ellipse([60 + k * 14 * u - 4, 46, 60 + k * 14 * u + 4, 54], fill=WHITE + (255,))
            blend(frame, np.array(im), W / 2 - 60, 1340, 1 - ease_in((t - (self.t1 - 0.3)) / 0.3))
