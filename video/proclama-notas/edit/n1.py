"""Nota 1 · Colombia rompe récord de masacres en la última década (reel vertical, Proclama del Pacífico).

python3 n1.py [--preview SEG]  -> out/n1_video.mp4 + out/n1_plan.json (tiempos para la mezcla de audio)
"""
import json
import sys

sys.path.insert(0, '/home/user/notas/edit')
import lib  # noqa: E402
from lib import ROOT, W, Shot, blur_band, blur_frame, render  # noqa: E402
from gfx import (Bajada, Counters, Credit, Gradients, ListCards, LogoBug, MapCO, Question, RaceChart,  # noqa: E402
                 TitleCard, Transition)

# Palabras sensibles: se censuran en pantalla (letra cambiada por *) para no perder alcance en redes.
lib.CENSOR.update({
    'masacres': 'm*sacres', 'masacre': 'm*sacre', 'asesinadas': 'as*sinadas', 'asesinados': 'as*sinados',
    'asesinatos': 'as*sinatos', 'crímenes': 'cr*menes', 'armado': 'arm*do', 'armados': 'arm*dos',
    'ilícitas': 'il*citas', 'ataques': 'at*ques', 'violencia': 'vi*lencia',
})

FB = ROOT + '/raw/fb/'
CAR = FB + '1779948513255633.mp4'   # Cauca Al Día · ataque con drones en El Carmelo (Cajibío)
VR = FB + '2189964538548536.mp4'    # Denuncias Ciudadanas Cali · peaje de Villa Rica
CAJ = FB + '1134117992883369.mp4'   # Cajamarca Real · peaje destruido (trae un texto quemado abajo)
MOR = FB + '1130547536626622.mp4'   # Tv Norte Noticias · ataque a la estación de Morales
# Son videos de ataques recientes en el Cauca (no de masacres): se rotulan como imágenes de referencia.
CREDIT = {k: 'Imágenes de referencia · ' + v for k, v in {
    CAR: 'Video: Cauca Al Día', VR: 'Video: Denuncias Ciudadanas Cali', CAJ: 'Video: Cajamarca Real',
    MOR: 'Video: Tv Norte Noticias'}.items()}


def rd(text, extra=0.0):
    n = len(text.replace('[', '').replace(']', ''))
    return round(0.85 + n / 16.5 + extra, 2)


def bg(f):
    return blur_frame(f, dark=0.55, tint=(90, 0, 0))


def hide_caption(f):
    return blur_band(f, 1150, 1500)


shots, ovs, plan = [], [], {'sfx': [], 'hits': [], 'sections': []}
T = 0.0


def add(shot):
    global T
    shots.append((T, shot))
    if shot.src in CREDIT and shot.post is not bg:
        ovs.append(Credit(CREDIT[shot.src], T + 0.05, T + shot.dur - 0.05))
    T += shot.dur


def seq(parts, total):
    """Reparte 'total' segundos entre varios planos (pesos relativos)."""
    wsum = sum(p[2] for p in parts)
    for src, tin, w, kw in parts:
        add(Shot(src, tin, round(total * w / wsum * 30) / 30, **kw))


# ------------------------------------------------------------------ gancho: titular
HOOK = 5.1
add(Shot(MOR, 4.8, HOOK, z0=1.0, z1=1.14, vol=-17))
title = TitleCard(['COLOMBIA ROMPE', '[RÉCORD] DE [MASACRES]', 'EN LA ÚLTIMA DÉCADA'], 0.15, HOOK, size=68, line_h=76)
plan['hits'].append(0.15)
tr_a = Transition('tr1', HOOK - 0.8)
plan['sfx'].append(('Transicion_1_PC', HOOK - 0.8, -12))
plan['sections'].append(('hook', 0.0))

body = []  # overlays del cuerpo (texto y gráficos)
B0 = T
plan['sections'].append(('body', B0))


def card(text, parts, extra=0.0, delay=0.3, **kw):
    t0 = T
    d = rd(text, extra) + delay
    seq(parts, d)
    body.append(Bajada(text, t0 + delay, t0 + d, **kw))
    return t0, d


# C1
card('Colombia enfrenta uno de los años más complejos en materia de seguridad de la última década.',
     [(CAR, 0.3, 3.0, dict(z0=1.0, z1=1.08, vol=-20)), (CAR, 8.6, 3.6, dict(z0=1.04, z1=1.12, vol=-20))], delay=0.65)
# C2
card('Según el Instituto de Estudios para el Desarrollo y la Paz, [Indepaz],',
     [(CAR, 47.0, 1, dict(z0=1.0, z1=1.25, focus=(0.5, 0.45), vol=-18))])
# C3 · contadores
t0 = T
txt = 'entre enero y octubre de 2026 se registraron [97 masacres], que dejaron [376 personas asesinadas].'
d = rd(txt, 1.0) + 0.3
seq([(CAJ, 0.8, 1, dict(z0=1.08, z1=1.0, post=bg))], d)
body.append(Counters([{'value': 97, 'label': 'MASACRES'}, {'value': 376, 'label': 'PERSONAS\\nASESINADAS'}],
                     t0, t0 + d, y=600, size=230, header=None,
                     footer='Del 1 de enero al 9 de octubre de 2026 · Fuente: Indepaz'))
body.append(Bajada(txt, t0 + 0.3, t0 + d))
plan['hits'] += [t0 + 0.15, t0 + 0.6]
# C4 + C5 · curva acumulada
t0 = T
a = 'La cifra supera los [96 casos] documentados en 2021 y los [94] de 2022,'
b = 'convirtiendo a 2026 en el año con [mayor número de masacres] desde la firma del acuerdo de paz en 2016.'
da, db = rd(a) + 0.2, rd(b, 0.6)
seq([(VR, 0.5, 1, dict(z0=1.0, z1=1.1, post=bg))], da + db)
body.append(RaceChart(t0, t0 + da + db, draw_dur=5.6))
body.append(Bajada(a, t0 + 0.3, t0 + da))
body.append(Bajada(b, t0 + da, t0 + da + db))
plan['hits'].append(t0 + 1.0 + 5.6 + 0.2)
# C6 · C7
card('Entre las víctimas se encuentran hombres, mujeres y [menores de edad],',
     [(CAJ, 1.0, 1, dict(z0=1.0, z1=1.08, post=hide_caption))])
card('mientras que decenas de personas aún [no han sido identificadas].',
     [(MOR, 9.6, 1, dict(z0=1.06, z1=1.0, vol=-19)), (CAJ, 13.6, 1, dict(z0=1.0, z1=1.1, post=hide_caption))])
# C8 · C9 · C10 · mapa
t0 = T
c8 = '[El Cauca] figura entre los territorios más afectados,'
c9 = 'con [14 masacres] y al menos [68 víctimas mortales] durante el periodo analizado.'
c10 = '[Antioquia] también registra una alta concentración de estos crímenes.'
d8, d9, d10 = rd(c8, 0.6) + 0.3, rd(c9, 0.4), rd(c10, 0.3)
seq([(CAR, 60.0, 1, dict(z0=1.0, z1=1.1, post=bg))], d8 + d9 + d10)
body.append(MapCO(t0, t0 + d8 + d9 + d10, t_cauca_label=t0 + d8, t_antioquia=t0 + d8 + d9))
body.append(Bajada(c8, t0 + 0.5, t0 + d8, bottom=1462))
body.append(Bajada(c9, t0 + d8, t0 + d8 + d9, bottom=1462))
body.append(Bajada(c10, t0 + d8 + d9, t0 + d8 + d9 + d10, bottom=1462))
plan['hits'] += [t0 + 0.6, t0 + d8, t0 + d8 + d9]
# C11 · factores (con cortinilla de Proclama antes)
plan['sfx'].append(('Transicion_2_PC', T - 1.2, -13))
tr_c = Transition('tr2', T - 1.2)
t0 = T
c11 = 'Según investigadores del conflicto armado, esta situación está relacionada con:'
items = ['Las disputas por el control territorial entre organizaciones ilegales.',
         'El crecimiento de las economías ilícitas.',
         'Las dificultades del Estado para garantizar la seguridad de las comunidades.']
items = [' '.join(lib.censor(w) for w in it.split()) for it in items]
d11 = rd(c11) + 0.6
ti = [t0 + 1.4, t0 + d11 + 0.6, t0 + d11 + 0.6 + 3.3]
dl = ti[2] - t0 + 4.6
seq([(VR, 3.6, 1, dict(z0=1.0, z1=1.08, post=lambda f: blur_frame(f, k=24, dark=0.5))),
     (VR, 12.3, 1, dict(z0=1.06, z1=1.0, post=lambda f: blur_frame(f, k=24, dark=0.5)))], dl)
body.append(Bajada(c11, t0 + 0.8, t0 + d11 + 0.6))
body.append(ListCards(items, ti, t0 + dl, y=640))
plan['hits'] += ti
# C15 · contadores desde 2016
t0 = T
txt = 'Desde 2016, Indepaz ha documentado [791 masacres] y cerca de [2.900 víctimas] en Colombia.'
d = rd(txt, 1.0) + 0.3
seq([(CAR, 30.0, 1, dict(z0=1.0, z1=1.08, post=bg))], d)
body.append(Counters([{'value': 791, 'label': 'MASACRES'}, {'value': 2900, 'label': 'VÍCTIMAS', 'prefix': '≈'}],
                     t0, t0 + d, y=720, size=150, header='DESDE LA FIRMA DEL [ACUERDO DE PAZ] (2016)',
                     footer='Fuente: Indepaz', cx=[W * 0.21, W * 0.655]))
body.append(Bajada(txt, t0 + 0.3, t0 + d))
plan['hits'] += [t0 + 0.15, t0 + 0.6]
# C16 · C17
card('Las cifras muestran la persistencia de una violencia que afecta tanto a las [zonas rurales] como a los '
     '[centros urbanos]', [(CAR, 15.4, 1, dict(z0=1.0, z1=1.08, vol=-20)),
                           (MOR, 5.0, 1, dict(z0=1.1, z1=1.0, vol=-19))])
card('y mantiene a miles de familias bajo el temor de nuevos ataques.',
     [(CAR, 76.0, 1, dict(z0=1.0, z1=1.3, focus=(0.5, 0.42), vol=-14))], extra=0.6)
# Pregunta final
t0 = T
dq = 7.2
seq([(CAR, 92.0, 1, dict(z0=1.0, z1=1.1, post=bg))], dq)
body.append(Question(['¿QUÉ DEBERÍA CAMBIAR', 'EN LAS [POLÍTICAS DE]', '[SEGURIDAD] PARA QUE SE', 'DEJEN DE REGISTRAR',
                      'TANTAS [MASACRES?]'], t0 + 0.2, t0 + dq))
plan['hits'].append(t0 + 0.2)
plan['sections'].append(('question', t0))
END_BODY = T
# Cierre de Proclama
tr_b = Transition('tr1', END_BODY - 0.8)
plan['sfx'].append(('Transicion_1_PC', END_BODY - 0.8, -12))
add(Shot(ROOT + '/raw/pc/Cierre_Vertical.mp4', 0.0, 4.1, z0=1.0, z1=1.0))
plan['sfx'].append(('cierre', END_BODY, -8))
plan['sections'].append(('cierre', END_BODY))
TOTAL = T

overlays = [Gradients(0, END_BODY)] + body + [title, LogoBug(0.2, END_BODY - 0.3, pulses=[38.6, 86.8]),
                                              tr_a, tr_c, tr_b]
# credits quedan bajo los gráficos pero sobre el degradado
creds = [o for o in ovs]
overlays = overlays[:1] + creds + overlays[1:]
plan['total'] = TOTAL
plan['end_body'] = END_BODY
plan['shots'] = [(t, s.src, s.t_in, s.dur, s.vol, getattr(s, 'speed', 1.0)) for t, s in shots]

if __name__ == '__main__':
    print(f'Duración total: {TOTAL:.2f}s ({len(shots)} planos)')
    json.dump(plan, open(ROOT + '/out/n1_plan.json', 'w'), indent=1)
    if '--plan' in sys.argv:
        sys.exit()
    if '--preview' in sys.argv:
        # renderiza solo un tramo [a, b] a baja calidad para revisar
        a, b = float(sys.argv[sys.argv.index('--preview') + 1]), float(sys.argv[sys.argv.index('--preview') + 2])
        sub = []
        for t, s in shots:
            if t + s.dur > a and t < b:
                sub.append((t, s))
        import copy
        sub2 = []
        for t, s in sub:
            s2 = copy.copy(s)
            if t < a:
                s2.t_in = s.t_in + (a - t) * getattr(s, 'speed', 1.0)
                s2.dur = s.dur - (a - t)
                s2.n = int(round(s2.dur * 30))
                t = a
            sub2.append((t - a, s2))

        class Shift:
            def __init__(self, o):
                self.o = o

            def draw(self, f, t):
                self.o.draw(f, t + a)
        render(sub2, [Shift(o) for o in overlays], ROOT + '/out/n1_preview.mp4', total=b - a, preset='veryfast',
               crf=22)
    else:
        render(shots, overlays, ROOT + '/out/n1_video.mp4', total=TOTAL)
