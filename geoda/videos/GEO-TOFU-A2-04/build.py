#!/usr/bin/env python3
"""GEO-TOFU-A2-04 · Podcast (host mujer + invitada mujer) · ~36 s · CTA principal K1 Black Friday (sin precio) + alterno K2 Navidad.
Voces NATIVAS de WAN 3.0 (labios sincronizados de origen): invitada en 2 tomas (la 2.ª se empareja en tono con la 1.ª,
timbre conservado), host en 1 toma. Cada frase usa su propio tramo del clip (plano y audio del mismo momento).
Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario; sin 'aclara'/'blanquea'; sin explicaciones médicas.
Versiones: HA y HB del brief con K1; HC y HD nuevos con K2 (de la toma 2 de la invitada)."""
import os, sys, subprocess, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
A = f'{G}/a204'; T = f'{A}/tmp'; os.makedirs(T, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
G1, G2, H = f'{HF}/wq_g1_0.mp4', f'{HF}/wq_g2_0.mp4', f'{HF}/wq_h_0.mp4'
CTA_BF, CTA_NAV = f'{G}/a108/tmp/cta_bf.mp4', f'{G}/a202/tmp/xmas_ec_bow.mp4'
PITCH = {G2: 0.917}   # toma 2 de la invitada un 9 % más aguda: se baja al tono de la toma 1 (formantes conservados)
PAD = 0.04
# (clip, inicio, fin, texto) medidos por energía y verificados transcribiendo cada frase sola
LINES = {
 'HA': (G1, 0.64, 4.11, 'Yo cambié tres cosas en mi rutina de axilas.'),
 'HB': (G1, 4.44, 9.21, 'Perfume, rasurada a la carrera y ropa apretada. Ese era mi combo.'),
 'HC': (G2, 13.29, 17.38, 'Este año voy a regalar lo que me cambió la rutina.'),
 'HD': (G2, 18.94, 22.16, 'Lo que nadie me cree de mi rutina de axilas.'),
 'B1': (H, 0.43, 2.25, 'Cuéntame qué cambiaste.'),
 'B2': (G1, 9.67, 12.66, 'Primero, el desodorante con perfume. Lo dejé.'),
 'B3': (H, 3.50, 4.26, '¿Por qué?'),
 'B4': (G1, 13.17, 15.30, 'Mi piel no lo quería más. Me picaba.'),
 'B5': (G1, 15.62, 17.88, 'Segundo, la rasurada a la carrera.'),
 'B6': (G1, 18.26, 21.19, 'Y tercero, la ropa súper apretada todo el día.'),
 'B7': (H, 5.87, 7.08, '¿Y qué usas ahora?'),
 'B8': (G1, 21.84, 26.71, 'Una piedra de alumbre. Es un mineral: la mojo y ya, sin perfume.'),
 'B9': (H, 8.98, 10.25, '¿Y sí se ve distinto?'),
 'B10': (G1, 26.87, 29.98, 'Yo las veo más parejas. A mí me funcionó.'),
 'B11': (H, 12.24, 15.02, 'Me la vas a prestar.'),
 'K1': (G2, 0.60, 6.10, 'Se llama GEODA, y por Black Friday: paga dos, lleva tres. Pagas cuando te llegue.'),
 'K2': (G2, 6.31, 12.81, 'Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.'),
}
GUEST_BOX = [(260, 560, 820, 1060)]    # cara de la invitada (con pelo), plano medio
HOST_BOX = [(300, 520, 860, 1040)]

def seg(k):
    clip, a0, a1, text = LINES[k]; return clip, max(0, a0 - PAD), a1 + PAD, text

def wav(name, clip, a0, d):
    af = (f'rubberband=pitch={PITCH[clip]}:formant=preserved,' if clip in PITCH else '') + f'apad=whole_dur={d:.3f}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a0:.3f}', '-t', f'{d:.3f}', '-i', clip, '-vn', '-ac', '1', '-ar', '48000',
                    '-af', af, f'{T}/{name}.wav'], check=True)

def row_shot(key, k, src=None, box=None, extra=0.0, **o):
    clip, a0, a1, text = seg(k); d = a1 - a0 + extra
    name = f'r_{key}_{k}' + ('_v' if src else '')
    if src:   # otro video (el cierre) con la voz de la frase
        sh = B.shot(T, name, src, d, **o)
    else:     # el mismo clip y tramo de la voz: labios sincronizados
        sh = B.shot(T, name, clip, d, ss=a0, **o)
    wav(name, clip, a0, d)
    words = [(w, t0 - a0, t1 - a0) for w, t0, t1 in B.word_times(text, LINES[k][1], LINES[k][2] - LINES[k][1])]
    return [sh + ((box,) if box is not None else ())], d, words

def plan(cta):
    rows = {'HA': ('HA', {}), 'HB': ('HB', {}), 'HC': ('HC', {}), 'HD': ('HD', {}),
            'B1': ('B1', dict(box=HOST_BOX)), 'B2': ('B2', dict(box=GUEST_BOX)), 'B3': ('B3', dict(box=HOST_BOX)),
            'B4': ('B4', dict(box=GUEST_BOX)), 'B5': ('B5', dict(box=GUEST_BOX)), 'B6': ('B6', dict(box=GUEST_BOX)),
            'B7': ('B7', dict(box=HOST_BOX)), 'B8': ('B8', dict(box=GUEST_BOX)), 'B9': ('B9', dict(box=HOST_BOX)),
            'B10': ('B10', dict(box=GUEST_BOX)), 'B11': ('B11', dict(box=HOST_BOX)),
            'B12': (cta, dict(src=CTA_BF if cta == 'K1' else CTA_NAV, extra=0.5, z0=1.0, z1=1.10, fx=0.5, fy=0.62,
                              box=[(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)] if cta == 'K1' else [(320, 940, 880, 1620)]))}
    shots, meta = {}, {}
    for key, (k, o) in rows.items():
        o = dict(o); o.setdefault('z0', 1.0); o.setdefault('z1', 1.05)
        if key == 'HD': o.update(z0=1.26, z1=1.29, fx=0.5, fy=0.0)   # zoom anclado arriba: la cabeza baja, lejos del título
        if key.startswith('H'): o.setdefault('box', [(200, 530, 840, 1210)] if key in ('HD',) else GUEST_BOX)   # HD: primer plano de la toma 2
        shots[key], d, wd = row_shot(key, k, **o); meta[key] = (d, wd)
    return shots, meta

def cfg_for(meta, cta):
    def row(key, **kw):
        d, wd = meta[key]
        return dict(key=key, clip_audio=True, dur=d, words=wd, line=' '.join(w for w, _, _ in wd), **kw)
    hooks = {
        'HA': row('HA', subs=False, text=('Lo que cambié en mi', 'rutina de axilas'), sfx=[(0.1, f'{AU}/sfx_thud.wav', 0.5)]),
        'HB': row('HB', subs=False, text=('Perfume, rasurada y roce:', 'mi combo fatal'), sfx=[(0.1, f'{AU}/sfx_error.wav', 0.25)]),
        'HC': row('HC', subs=False, text=('Este año voy a regalar', 'lo que me cambió 🎁')),
        'HD': row('HD', subs=False, text=('Lo que nadie me cree', 'de mi rutina de axilas'), hook_slots=[356], hook_maxw=680),   # primer plano: título más arriba, lejos del pelo
    }
    for h in hooks.values(): h.pop('key')
    body = [row('B1'), row('B2', big='1'), row('B3'), row('B4'), row('B5', big='2'), row('B6', big='3'), row('B7'),
            row('B8', sfx=[(1.8, f'{AU}/splash_1180.mp3', 0.25)]), row('B9'), row('B10'), row('B11'),
            row('B12', sfx=[(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)] if cta == 'K1' else [])]
    ctad = dict(row='B12', delay=0.2, l1='BLACK FRIDAY', l2='Paga 2 lleva 3') if cta == 'K1' else dict(row='B12', delay=0.2, l1='REGALO DE NAVIDAD', l2='Paga 2 lleva 3')
    return dict(id='GEO_TOFU_A2_04', fmt='PODCAST' if cta == 'K1' else 'PODCAST_K2', version=1, tmp=T, out_dir=A, vo_dir=T,
                min_face=50, hook_text_until=3.0, ai_label=False, cut_sfx=True, cut_sfx_vol=0.10, music=f'{AU}/music_847.mp3', music_vol=0.06,
                hooks=hooks, body=body, cta=ctad)

if __name__ == '__main__':
    want = sys.argv[1:] or ['HA', 'HB', 'HC', 'HD']
    for cta, hks in (('K1', ['HA', 'HB']), ('K2', ['HC', 'HD'])):
        hks = [h for h in hks if h in want]
        if not hks: continue
        shots, meta = plan(cta); cfg = cfg_for(meta, cta)
        for hk in hks:
            B.build(cfg, hk, shots)
