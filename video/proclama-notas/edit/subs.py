"""Subtítulos de entrevistas: alinea el texto corregido a mano con los tiempos de Whisper palabra por palabra."""
import difflib
import json
import re

import numpy as np

from lib import FPS, W, blend, clamp, ease_out, font, layout, word_sprite, WHITE, RED


def norm(w):
    return re.sub(r'[^\wáéíóúñü]', '', w.lower())


def align(transcript, t_in, t_out, text):
    """Devuelve [(palabra, inicio, fin)] (en segundos de la fuente) para el texto corregido."""
    d = json.load(open(transcript))
    ww = [w for s in d['segments'] for w in s['words'] if t_in - 0.3 <= w['s'] <= t_out + 0.1]
    src = [norm(w['w']) for w in ww]
    dst = text.split()
    dn = [norm(w) for w in dst]
    sm = difflib.SequenceMatcher(None, src, dn, autojunk=False)
    times = [None] * len(dst)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            times[b + k] = (ww[a + k]['s'], ww[a + k]['e'])
    # interpola las palabras sin pareja
    known = [i for i, t in enumerate(times) if t]
    if not known:
        span = np.linspace(t_in, t_out, len(dst) + 1)
        return [(w, span[i], span[i + 1]) for i, w in enumerate(dst)]
    for i in range(len(dst)):
        if times[i] is None:
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            a = times[prev][1] if prev is not None else t_in
            b = times[nxt][0] if nxt is not None else t_out
            gap_idx = [j for j in range(len(dst)) if (prev is None or j > prev) and (nxt is None or j < nxt)]
            pos = gap_idx.index(i)
            step = (b - a) / max(1, len(gap_idx))
            times[i] = (a + pos * step, a + (pos + 1) * step)
    return [(w, max(t_in, s), min(t_out, e)) for w, (s, e) in zip(dst, times)]


def chunks(words, max_chars=34, max_lines=2):
    """Agrupa palabras en tarjetas de hasta 2 renglones, cortando preferentemente en puntuación."""
    cards, cur = [], []
    limit = max_chars * max_lines
    for i, (w, s, e) in enumerate(words):
        cur.append((w, s, e))
        txt = ' '.join(x[0] for x in cur)
        nxt = words[i + 1][0] if i + 1 < len(words) else ''
        end_punct = w[-1] in '.,;:?!' and len(txt) > limit * 0.45
        if len(txt) + 1 + len(nxt) > limit or end_punct or not nxt:
            cards.append(cur)
            cur = []
    return cards


class Subtitles:
    """Subtítulos de una entrevista en la línea de tiempo: tarjetas de 1–2 renglones sobre una caja oscura."""

    def __init__(self, transcript, t_in, t_out, text, t_tl, bottom=1385, size=44, line_h=58):
        self.words = align(transcript, t_in, t_out, text)
        self.fnt = font('Poppins-SemiBold', size)
        self.cards = []
        cs = chunks(self.words)
        for k, c in enumerate(cs):
            s = t_tl + (c[0][1] - t_in)
            e = t_tl + ((cs[k + 1][0][1] if k + 1 < len(cs) else c[-1][2] + 0.35) - t_in)
            e = min(e, t_tl + (t_out - t_in))
            txt = ' '.join(x[0] for x in c)
            items, hgt, nl = layout(txt, self.fnt, W - 180, line_h, align='center')
            lines = {}
            for (x, y, w, st, ww, li) in items:
                lines.setdefault(li, []).append((x, w, ww))
            sprites = []
            from PIL import Image, ImageDraw
            im = Image.new('RGBA', (W, hgt + 40), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for li, ws in lines.items():
                x0 = 90 + ws[0][0] - 18
                x1 = 90 + ws[-1][0] + ws[-1][2] + 18
                y0 = 20 + li * line_h - 4
                d.rounded_rectangle([x0, y0, x1, y0 + line_h], 10, fill=(0, 0, 0, 165))
            for (x, y, w, st, ww, li) in items:
                d.text((90 + x, 20 + y + 2), w, font=self.fnt, fill=WHITE + (255,))
            self.cards.append((s, e, np.array(im), bottom - hgt - 20))

    def draw(self, frame, t):
        for s, e, spr, y in self.cards:
            if s <= t < e:
                a = clamp((t - s) / 0.08)
                blend(frame, spr, 0, y, a)


class Rotulo:
    """Rótulo de nombre de Proclama (Rotulo_Nombre_PC_2026.mov) con nombre y cargo."""

    def __init__(self, name, role, t0, dur=4.2):
        from lib import ASSETS, Seq, NAVY
        from PIL import Image, ImageDraw
        self.seq = Seq(ASSETS + '/rotulo')
        self.t0, self.dur = t0, dur
        fn, fr = font('Roboto-Black', 40), font('Roboto-Light', 31)
        if fn.getlength(name.upper()) > 760:
            fn = font('Roboto-Black', 34)
        im = Image.new('RGBA', (900, 240), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.text((72, 58), name.upper(), font=fn, fill=NAVY + (255,))
        d.text((73, 112), role, font=fr, fill=NAVY + (255,))
        self.text = np.array(im)

    def draw(self, frame, t):
        u = t - self.t0
        if u < 0 or u > self.dur:
            return
        k = int(u * FPS)
        out_start = self.dur - 0.9
        if u < out_start:
            idx = min(k, 30)
        else:
            idx = 290 + int((u - out_start) * FPS)
        blend(frame, self.seq.get(idx), 90, 1385)
        a = clamp((u - 1.0) / 0.25) * (1 - clamp((u - out_start) / 0.15))
        if a > 0:
            dx = -20 * (1 - ease_out((u - 1.0) / 0.35))
            blend(frame, self.text, 90 + dx, 1385, a)
