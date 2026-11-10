"""Nota 2 · Entrega de compactadores y seguimiento a obras en Santander de Quilichao (reel vertical).

Material grabado por Proclama del Pacífico el 2 de julio de 2026. Sin locutor: textos en pantalla + entrevistas
con subtítulos y rótulo de nombre de Proclama.
python3 n2.py [--plan]
"""
import json
import sys

sys.path.insert(0, '/home/user/notas/edit')
from lib import ROOT, W, Shot, blur_frame, render  # noqa: E402
from gfx import Bajada, Gradients, LogoBug, Question, TitleCard, Transition  # noqa: E402
from subs import Rotulo, Subtitles  # noqa: E402

RAW = ROOT + '/raw/n2/'
TR = ROOT + '/work/n2/tr/'


def dj(code):
    import glob
    return glob.glob(RAW + f'dji/DJI_*_{code}_D.MP4')[0]


INT = {
    'gob1': ('Octavio_Guzman__solo_primera_pregunta.mp4', 'Octavio Guzmán', 'Gobernador del Cauca'),
    'gob5': ('Gobernador_del_Cauca__Octavio_Gzman.mp4', 'Octavio Guzmán', 'Gobernador del Cauca'),
    'mac': ('Jorge_Macas__gerente_de_Emcaservicios.mp4', 'Jorge Macías', 'Gerente de Emcaservicios'),
    'gri': ('Alcalde_de_Santander_de_Quilichao__Luis_Eduardo_Grijalba.mp4', 'Luis Eduardo Grijalba',
            'Alcalde de Santander de Quilichao'),
    'inz': ('Delio_Hernn_Trujillo__alcalde_de_Inz.mp4', 'Delio Hernán Trujillo', 'Alcalde de Inzá'),
    'cam': ('Carolina_Camargo__secretaria_de_Salud_del_Cauca.mp4', 'Carolina Camargo', 'Secretaria de Salud del Cauca'),
}


def ipath(k):
    return RAW + 'int/' + INT[k][0]


def tpath(k):
    return TR + INT[k][0].rsplit('.', 1)[0] + '.json'


shots, top, body, plan = [], [], [], {'sfx': [], 'hits': [], 'sections': [], 'voices': []}
T = 0.0


def add(shot):
    global T
    shots.append((T, shot))
    T += shot.dur


def broll(code, tin, dur, **kw):
    kw.setdefault('vol', -24)
    kw.setdefault('z0', 1.0)
    kw.setdefault('z1', 1.07)
    add(Shot(dj(code) if not code.startswith('/') else code, tin, dur, **kw))


def rd(text, extra=0.0):
    n = len(text.replace('[', '').replace(']', ''))
    return round(0.85 + n / 16.5 + extra, 2)


def card(text, parts, delay=0.3, extra=0.0):
    """Texto del guion sobre una secuencia de planos de apoyo [(clip, entrada, peso, kw)]."""
    t0 = T
    d = rd(text, extra) + delay
    wsum = sum(p[2] for p in parts)
    for code, tin, w, kw in parts:
        broll(code, tin, round(d * w / wsum * 30) / 30, **kw)
    body.append(Bajada(text, t0 + delay, t0 + d))
    return t0, d


def sot(key, bites, cutaways=(), rotulo=True, z=(1.0, 1.04)):
    """Entrevista: bites = [(entrada, salida, texto corregido)], encadenados con corte (salto con zoom).
    cutaways = [(desde_s_relativo, dur, clip, entrada_clip)]: planos de apoyo encima de la voz."""
    global T
    t0 = T
    src = ipath(key)
    tl = T
    segs = []
    for k, (a, b, text) in enumerate(bites):
        zz = (z[0], z[1]) if k % 2 == 0 else (1.12, 1.15)
        segs.append((tl, a, b, zz))
        body.append(Subtitles(tpath(key), a, b, text, tl))
        plan['voices'].append([tl, src, a, b - a, 0.0])
        tl += b - a
    total = tl - t0
    # video: la entrevista, interrumpida por planos de apoyo
    cuts = sorted(cutaways)
    events = []
    for (tl_s, a, b, zz) in segs:
        events.append(('int', tl_s, tl_s + (b - a), a, zz))
    timeline = []
    for kind, s, e, a, zz in events:
        cur = s
        for (cs, cd, clip, cin) in cuts:
            cs_abs = t0 + cs
            if cs_abs >= e or cs_abs + cd <= cur:
                continue
            if cs_abs > cur:
                timeline.append(('int', cur, cs_abs, a + (cur - s), zz))
            ce = min(e, cs_abs + cd)
            timeline.append(('b', max(cur, cs_abs), ce, clip, cin + max(0, cur - cs_abs)))
            cur = ce
        if cur < e - 1e-3:
            timeline.append(('int', cur, e, a + (cur - s), zz))
    for item in timeline:
        if item[0] == 'int':
            _, s, e, a, zz = item
            add(Shot(src, a, round((e - s) * 30) / 30, z0=zz[0], z1=zz[1], focus=(0.5, 0.42)))
        else:
            _, s, e, clip, cin = item
            broll(clip, cin, round((e - s) * 30) / 30, vol=None)
    T = t0 + total
    # el redondeo de cuadros puede desplazar T: se corrige al total exacto
    T = shots[-1][0] + shots[-1][1].dur
    if rotulo:
        _, name, role = INT[key]
        first_cut = min([c[0] for c in cuts], default=99)
        body.append(Rotulo(name, role, t0 + 0.3, dur=min(4.2, total - 0.5, first_cut - 0.4)))
    return t0, total


# ------------------------------------------------------------------ gancho
HOOK = 5.0
broll('0165', 20.0, HOOK, z0=1.0, z1=1.12)
title = TitleCard(['[4 COMPACTADORES]', 'PARA SANTANDER,', 'CALOTO E INZÁ'], 0.15, HOOK, size=70, line_h=78)
top.append(Transition('tr1', HOOK - 0.8))
plan['sfx'].append(('Transicion_1_PC', HOOK - 0.8, -10))
plan['hits'].append(0.15)
B0 = T

# ------------------------------------------------------------------ compactadores
card('La Gobernación del Cauca, a través de Emcaservicios, entregó [cuatro vehículos compactadores] en Santander de '
     'Quilichao.', [('0135', 0.5, 1, {}), ('0132', 1.0, 1, {}), ('0136', 0.3, 1, {})], delay=0.6)
sot('gob1', [(19.42, 33.70, 'Es importante destacar que a través de estos vehículos compactadores vamos a poder hacer '
              'una recolección eficiente de los residuos sólidos, pero también mitigar ese impacto ambiental que '
              'generan estos residuos cuando no se recogen.')],
    cutaways=[(5.2, 3.4, '0133', 0.3)])
card('[Dos] son para Santander de Quilichao y los otros dos, para [Caloto] e [Inzá].',
     [('0142', 0.2, 1, {}), ('0140', 0.2, 1, {}), ('0141', 0.1, 1, {})])
sot('mac', [(31.62, 44.95, 'Decirles que Santander va a recibir dos vehículos, uno de 25 yardas, el cual llamamos el '
             'popular doble troque, y uno, un camión sencillo de 17 yardas para la recolección no solamente de '
             'Santander, sino de Mondomo y sus alrededores.')],
    cutaways=[(4.6, 4.0, '0137', 0.3)])
sot('gri', [(31.50, 40.10, 'Hemos logrado gestionar con la Gobernación del departamento la compra de dos '
             'compactadores para recolección de basura, que suman unos 3.000 millones de pesos los dos.'),
            (44.20, 50.85, 'Habíamos venido presentando muchos problemas porque teníamos unos carros totalmente '
             'obsoletos, con uso de más de 20 años.'),
            (58.45, 67.75, 'Hoy, con alegría, con entusiasmo, le tenemos que decir al pueblo quilichagüeño que eso '
             'ya no va a volver a pasar: las basuras no se van a quedar en la calle de un día para otro.')],
    cutaways=[(8.6, 3.4, '0157', 0.5), (15.25, 2.6, '0143', 0.2)])
sot('inz', [(96.30, 105.95, 'Tenemos un problema, y es que lo público no es de nadie y entonces nadie lo cuida. '
             'Al contrario, lo público es de todos y por eso debemos cuidarlo aún más.')])
# corte de cinta con sonido ambiente
broll('0169', 10.0, 3.2, vol=-16)
END_A = T

# ------------------------------------------------------------------ hospital
top.append(Transition('tr2', T - 1.2))
plan['sfx'].append(('Transicion_2_PC', T - 1.2, -12))
plan['sections'].append(('hospital', T))
t0 = T
chap = TitleCard(['[SEGUIMIENTO A OBRAS]', 'HOSPITAL FRANCISCO', 'DE PAULA SANTANDER'], t0 + 0.75, t0 + 3.2, size=62,
                 line_h=70, url=False, bottom=1300)
body.append(chap)
broll('0179', 0.5, 3.2)
card('La comitiva también visitó el nuevo [Hospital Francisco de Paula Santander], donde ya se entregó el primer '
     'pabellón.', [('0181', 0.3, 1, {}), ('0174', 0.3, 1, {}), ('0175', 0.2, 1, {})], delay=0.2)
sot('cam', [(67.55, 77.85, 'Esta primera fase, que tiene el servicio de consulta externa, fisioterapia, laboratorio '
             'clínico y el área administrativa, abrirá las puertas a todos ustedes para que sean atendidos allí.'),
            (92.60, 97.75, 'Así que en el marco de más o menos un mes y medio o dos meses, la gente ya puede venir a '
             'consultar.')],
    cutaways=[(4.8, 3.0, '0178', 0.3), (7.8, 2.5, '0176', 0.3)])

# ------------------------------------------------------------------ calle 5
top.append(Transition('tr1', T - 0.8))
plan['sfx'].append(('Transicion_1_PC', T - 0.8, -12))
plan['sections'].append(('calle5', T))
t0 = T
chap2 = TitleCard(['[SEGUIMIENTO A OBRAS]', 'CALLE 5'], t0 + 0.55, t0 + 2.8, size=62, line_h=70, url=False,
                  bottom=1300)
body.append(chap2)
broll('0215', 0.3, 2.8)
card('En la [Calle 5], el gobernador y el alcalde revisaron con el contratista el avance de la obra.',
     [('0214', 0.3, 1, {}), ('0213', 0.3, 1, {})], delay=0.2)
sot('gob5', [(51.90, 58.20, 'Miramos cómo se avanza en las zonas de los andenes, de la ciclorruta y de la '
              'pavimentación.'),
             (70.80, 80.20, 'Decirle a la comunidad de Santander de Quilichao que es una obra que se va a terminar, '
              'que tiene el cierre financiero; les pedimos la comprensión y la paciencia.')],
    cutaways=[(4.6, 1.7, '0215', 3.5)])

# ------------------------------------------------------------------ cierre
t0 = T
dq = 6.4
broll('0167', 12.0, dq, vol=-22, post=lambda f: blur_frame(f, dark=0.55, tint=(90, 0, 0)))
body.append(Question(['¿QUÉ OPINAS DE', 'ESTAS [INVERSIONES]', 'PARA EL NORTE', 'DEL [CAUCA?]'], t0 + 0.2, t0 + dq))
plan['hits'].append(t0 + 0.2)
END_BODY = T
top.append(Transition('tr1', END_BODY - 0.8))
plan['sfx'].append(('Transicion_1_PC', END_BODY - 0.8, -10))
add(Shot(ROOT + '/raw/pc/Cierre_Vertical.mp4', 0.0, 4.1, z0=1.0, z1=1.0))
plan['sfx'].append(('cierre', END_BODY, -5))
TOTAL = T

overlays = [Gradients(0, END_BODY, bottom=0.78, bottom_from=1060)] + body + [title, LogoBug(0.2, END_BODY - 0.3,
                                                                                            pulses=[]), *top]
plan['total'] = TOTAL
plan['end_body'] = END_BODY
plan['sections'] = [('hook', 0.0), ('body', B0)] + plan['sections'] + [('question', t0), ('cierre', END_BODY)]
plan['shots'] = [(t, s.src, s.t_in, s.dur, s.vol, getattr(s, 'speed', 1.0)) for t, s in shots]
plan['duck'] = 0.7
plan['nat_boost'] = 10.0

if __name__ == '__main__':
    print(f'Duración total: {TOTAL:.2f}s ({len(shots)} planos)')
    json.dump(plan, open(ROOT + '/out/n2_plan.json', 'w'), indent=1)
    if '--plan' in sys.argv:
        for t, s in shots:
            print(f'{t:7.2f} {s.dur:5.2f} {s.src.split("/")[-1][:40]:40s} in={s.t_in:.2f} vol={s.vol}')
        sys.exit()
    render(shots, overlays, ROOT + '/out/n2_video.mp4', total=TOTAL)
