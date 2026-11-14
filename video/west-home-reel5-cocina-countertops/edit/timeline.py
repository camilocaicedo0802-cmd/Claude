"""Reel 5 — "Opciones para tu cocina": granite vs quartz countertops with Félix (1080x1920, 30 fps). Output seconds.

POV interview (Samantha asks off camera, her hand in the foreground), cut like the reference (estilo.md):
jump cuts that alternate wide / tight punch-in, B-roll + split screens on every option, no music bed.
"""
import glob, os
FPS = 30
W, H = 1080, 1920
ROOT = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel5/'
RAW = ROOT + 'dl/raw/'
PH = ROOT + 'photos/'          # stock photos prepared at IWxIH
TAIL = 0.45

# (take, src_in, src_out, gap_after) — cut points snapped to energy dips (tools/cuts.py)
_PIECES = [
    ('IMG_5382', 0.44, 5.05, 0.08),   # 0  Félix, ¿qué pasa si quiero remodelar mi cocina y no sé qué countertop elegir?
    ('IMG_5384', 4.97, 6.13, 0.0),    # 1  Tenemos dos opciones,
    ('IMG_5384', 7.36, 9.03, 0.08),   # 2  el granito o el cuarzo.
    ('IMG_5391', 6.86, 9.11, 0.08),   # 3  ¿Cuál es la diferencia entre los dos materiales?
    ('IMG_5393', 3.24, 6.91, 0.08),   # 4  El granito puede ser un poco más económico, pero requiere mayor mantenimiento.
    ('IMG_5393', 11.74, 14.20, 0.04), # 5  El cuarzo es un material fabricado,
    ('IMG_5393', 14.57, 16.56, 0.06), # 6  hay más variación en los patrones.
    ('IMG_5393', 17.10, 19.60, 0.08), # 7  Lo mejor de todo es que ya viene completamente sellado.
    ('IMG_5396', 8.21, 17.90, 0.08),  # 8  El cuarzo resiste calor, pero no tanto como el granito, entonces tienes que ser
                                      #    cuidadoso a la hora de usar tus ollas calientes, no dejarlas encima de tu countertop
                                      #    porque se puede dañar.
    ('IMG_5399', 4.69, 6.30, 0.08),   # 9  ¿Qué opción me recomendarías tú?
    ('IMG_5400', 13.28, 15.11, 0.0),  # 10 Hacemos un appointment y vamos a
    ('IMG_5400', 15.71, 17.71, 0.06), # 11 un distribuidor de materiales
    ('IMG_5400', 23.23, 26.50, 0.10), # 12 porque no es lo mismo mirarla completo a mirar un sample pequeño.
    ('IMG_5402', 1.22, 2.85, 0.0),    # 13 Y si quieres que mi equipo y yo te ayudemos,
    ('IMG_5402', 4.84, 7.65, 0.0),    # 14 comenta la palabra cocina y nos pondremos en contacto contigo.
]
VOICE = []
t = 0.0
for name, si, so, gap in _PIECES:
    VOICE.append((RAW + name + '.MOV', si, so, round(t, 3)))
    t += so - si + gap
DUR = round(t - _PIECES[-1][3] + TAIL, 2)


def vs(k):
    return VOICE[k][3]


def ve(k):
    return round(VOICE[k][3] + VOICE[k][2] - VOICE[k][1], 3)


def vt(k, src):
    return round(VOICE[k][3] + src - VOICE[k][1], 3)


def sync(k, t0, t1, **kw):
    clip, si, so, tp = VOICE[k]
    return dict(src=clip, t0=t0, t1=t1, src_in=si + (t0 - tp), speed=1.0, person=True, grade='kitchen', **kw)


WIDE = dict(zoom=[(0, 1.02), (1, 1.06)], cy=0.0)
TIGHT = dict(zoom=[(0, 1.42), (1, 1.46)], cy=-0.12)         # punch-in on Félix, chest up, headroom for subtitles
P = lambda n: PH + n + '.png'


def photo(name, t0, t1, zoom=((0, 1.04), (1, 1.12)), **kw):
    return dict(src=P(name), t0=t0, t1=t1, src_in=0, speed=0, grade='stock', zoom=list(zoom), **kw)


# times of a few key words (output seconds; see overlays.wk for the full word map)
SPLIT1 = vt(2, 7.36)                  # "el granito o el cuarzo" — split screen
CLEAN = 11.86                         # "pero requiere mayor mantenimiento"
HEAT_CMP = 22.56                      # "pero no tanto como el granito"
STEAM = vt(8, 11.83)                  # "entonces tienes que ser cuidadoso..."
POTS = vt(8, 14.76)                   # "no dejarlas encima de tu countertop porque se puede dañar"
SLAB_FULL = vs(12)                    # "porque no es lo mismo mirarla completo..."
SHOTS = [
    # HOOK — Félix on camera from frame 1, Samantha asks off camera
    sync(0, 0.0, 2.02, **WIDE),
    sync(0, 2.02, vs(1), **TIGHT),
    sync(1, vs(1), SPLIT1, zoom=[(0, 1.10), (1, 1.14)], cy=-0.02),
    # "el granito o el cuarzo" — split screen (drawn by overlays.Split over this plate)
    photo('granite_kitchen', SPLIT1, vs(3), person=False),
    # "¿Cuál es la diferencia entre los dos materiales?" — Félix listening, tight
    sync(3, vs(3), vs(4), **TIGHT),
    # "El granito puede ser un poco más económico" — wide, price bars over the cabinets
    sync(4, vs(4), CLEAN, **WIDE),
    # "pero requiere mayor mantenimiento" — natural granite up close (+ spray badge)
    photo('granite_colorful', CLEAN, vs(5), zoom=((0, 1.16), (1, 1.06))),
    # "El cuarzo es un material fabricado" — quartz kitchen
    photo('quartz_kitchen2', vs(5), vs(6), zoom=((0, 1.04), (1, 1.14))),
    # "hay más variación en los patrones" — pattern strips (overlays.Patterns over this plate)
    photo('quartz_pattern', vs(6), vs(7)),
    # "Lo mejor de todo es que ya viene completamente sellado" — tight
    sync(7, vs(7), vs(8), **TIGHT),
    # "El cuarzo resiste calor" — wide
    sync(8, vs(8), HEAT_CMP, **WIDE),
    # "pero no tanto como el granito" — split screen with heat bars
    photo('granite_texture', HEAT_CMP, STEAM, person=False),
    # "entonces tienes que ser cuidadoso a la hora de usar tus ollas calientes" — steam
    photo('steam_pan', STEAM, POTS, zoom=((0, 1.06), (1, 1.16))),
    # "no dejarlas encima de tu countertop porque se puede dañar" — pots on the island, red warning glow
    photo('hot_pots_island', POTS, vs(9), zoom=((0, 1.14), (1, 1.04))),
    # "¿Qué opción me recomendarías tú?" — warm light-leak back to Félix, tight
    sync(9, vs(9), vs(10), **TIGHT),               # + overlays.Leak
    # "Hacemos un appointment y vamos a" — wide
    sync(10, vs(10), vs(11), **WIDE),
    # "un distribuidor de materiales" — a showroom wall of slabs
    photo('granite_texture', vs(11), SLAB_FULL),   # covered by overlays.Grid (showroom wall)
    # "porque no es lo mismo mirarla completo a mirar un sample pequeño" — full slab that shrinks to a sample
    photo('slab_closeup', SLAB_FULL, vs(13), zoom=((0, 1.02), (1, 1.08))),
    # CTA — "Y si quieres que mi equipo y yo te ayudemos, comenta la palabra cocina..."
    sync(13, vs(13), vs(14), **WIDE),
    sync(14, vs(14), DUR, zoom=[(0, 1.06), (1, 1.10)], cy=-0.01),
]
PHOTOS = ['granite_kitchen', 'granite_texture', 'quartz_kitchen', 'quartz_kitchen2', 'quartz_pattern', 'cleaning_counter',
          'steam_pan', 'hot_pots_island', 'slabs_warehouse', 'slab_closeup', 'small_sample', 'granite_colorful',
          'quartz_white_detail']

if __name__ == '__main__':
    for k, v in enumerate(VOICE):
        print(k, os.path.basename(v[0]), v[1:], ve(k))
    print('DUR', DUR)
    for i, s in enumerate(SHOTS):
        assert s['t1'] > s['t0'] + 0.2, (i, s['t0'], s['t1'])
        if i:
            assert abs(SHOTS[i - 1]['t1'] - s['t0']) < 1e-6, (i, SHOTS[i - 1]['t1'], s['t0'])
        print(i, os.path.basename(s['src']), s['t0'], s['t1'], round(s['t1'] - s['t0'], 2))
