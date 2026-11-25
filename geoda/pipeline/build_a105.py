#!/usr/bin/env python3
"""GEO-MOFU-A1-05 · Podcast (host hombre + invitada mujer; la invitada es la voz principal).
Voces nativas de WAN 3.0: un clip largo por personaje (misma voz en todo el video). Etiqueta real en todas las tomas."""
import os, sys, json, subprocess, re
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.path.insert(0, G); sys.path.insert(0, f'{G}/tools')
import builder as B
A = f'{G}/a105'; T = f'{A}/tmp'; os.makedirs(T, exist_ok=True)
HF, S, AU = f'{G}/hf', f'{G}/stock', f'{G}/audio'
HOST, G1, G2 = f'{HF}/fixed/w_host_0.mp4', f'{HF}/fixed/w_g1_0.mp4', f'{HF}/fixed/w_g2_0.mp4'
G1H = f'{HF}/fixed/w_g1_nofit_0.mp4'   # stick en la mano (inclinado): etiqueta que sigue el giro; G1 (ajustada al tubo) sobre la mesa
# Frases del guion con sus tiempos REALES en cada clip (pausas medidas por energía y cada frase verificada transcribiéndola
# sola: dice exactamente el guion, sin palabras de la frase vecina). (texto, inicio, fin) de cada tramo de voz.
LINES = {
 'H0': (HOST, 0.70, 3.41, [('¿Por qué tanta gente dice que la piedra de alumbre no sirve?', 0.76, 3.35)]),
 'H1': (HOST, 3.64, 5.83, [('En serio, ¿por qué todo el mundo dice que no sirve?', 3.70, 5.77)]),
 'H2': (HOST, 6.57, 7.52, [('A ver, explícame.', 6.63, 7.46)]),
 'H3': (HOST, 8.26, 10.29, [('¿Y entonces por qué le falla a tanta gente?', 8.32, 10.23)]),
 'H4': (HOST, 11.12, 12.40, [('¿Y uno deja de sudar?', 11.27, 12.32)]),
 'H5': (HOST, 16.23, 17.41, [('¿Y si a mí no me funciona?', 16.29, 17.35)]),
 'G0': (G1, 0.25, 2.24, [('El problema casi nunca es la piedra.', 0.31, 2.18)]),
 'G1a': (G1, 2.59, 5.75, [('Porque el problema casi nunca es la piedra.', 2.65, 4.58), ('Es cómo la usan.', 4.83, 5.69)]),
 'G2l': (G1, 6.87, 10.72, [('El olor no es el sudor.', 6.93, 8.29), ('Es lo que pasa con el sudor en la piel.', 8.96, 10.66)]),
 'G3': (G1, 11.01, 15.85, [('El perfume lo tapa.', 11.07, 12.42), ('La piedra ayuda a neutralizarlo,', 12.75, 14.77), ('sin perfume.', 14.96, 15.79)]),
 'E1': (G2, 0.22, 3.04, [('Error uno: usarla seca.', 0.28, 1.87), ('Se moja la piedra.', 1.99, 2.99)]),
 'E2': (G2, 3.04, 5.99, [('Error dos: saltarse días.', 3.10, 4.76), ('Hay que ser constante.', 4.92, 5.93)]),
 'N':  (G2, 6.02, 9.45, [('No. No es antitranspirante.', 6.08, 7.76), ('Sigues sudando, pero sin olor.', 7.86, 9.39)]),
 'T':  (G2, 9.45, 12.88, [('Tienes 14 días: si no te funciona, te devuelven la plata.', 9.51, 12.82)]),
 'C':  (G2, 13.46, 16.73, [('No pagas nada ahora: pagas cuando te llegue.', 13.52, 16.67)]),
}
def words_of(key):
    clip, a0, a1, pieces = LINES[key]; out = []
    for text, s, e in pieces:
        out += [(w, t0 - a0, t1 - a0) for w, t0, t1 in B.word_times(text, s, e - s)]
    return out

PITCH = {G2: 1.035}   # la parte 2 de la invitada sale un poco más grave: se empareja con la parte 1 (timbre conservado)
def wav(name, clip, a0, d):
    af = (f'rubberband=pitch={PITCH[clip]}:formant=preserved,' if clip in PITCH else '') + f'apad=whole_dur={d:.3f}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a0:.3f}', '-t', f'{d:.3f}', '-i', clip, '-vn', '-ac', '1', '-ar', '48000',
                    '-af', af, f'{T}/{name}.wav'], check=True)

# fila = (clave, frase, [tomas]); toma: (nombre, tipo, fuente, duración o None=resto, opciones)
#   'sync' = el mismo clip y tramo de la voz (labios sincronizados); 'vid' = otro video (la voz sigue); 'still' = imagen fija
ROWS = {
 'HA':  ('H0', [('ha', 'sync', HOST, None, dict(z0=1.0, z1=1.04, shake=(0.0, 0.35, 16)))]),
 'HB':  ('G0', [('hb', 'vid', G1H, None, dict(ss='a0', z0=1.0, z1=1.04))]),
 'B1':  ('H1', [('b1', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B2':  ('G1a', [('b2a', 'vid', f'{HF}/k_set_0.mp4', 1.59, dict(ss=1.4, speed=0.85, z0=1.0, z1=1.04)),  # plano general: solo el tramo en que habla ella (él calla)
                 ('b2b', 'vid', HOST, None, dict(ss=13.35, speed=0.8, z0=1.0, z1=1.03))]),          # el host escucha (boca quieta 12,5-14,6 s)
 'B3':  ('H2', [('b3', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),                       # 'A ver, explícame' en su primer plano
 'B4':  ('G2l', [('b4', 'vid', f'{T}/ins_gota.mp4', None, dict(ss=0.0))]),
 'B5':  ('G3', [('b5a', 'still', f'{HF}/p_mesa_0.png', 2.4, dict(z0=1.0, z1=1.06)), ('b5b', 'sync', G1, None, dict(z0=1.04, z1=1.07))]),
 'B6':  ('H3', [('b6', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B7':  ('E1', [('b7a', 'sync', G2, 0.9, dict(z0=1.0, z1=1.03)), ('b7b', 'vid', f'{HF}/fixed/k_grifo2_0.mp4', None, dict(ss=0.6, z0=1.0, z1=1.05))]),
 'B8':  ('E2', [('b8', 'vid', f'{T}/ins_cal.mp4', None, dict(ss=0.0))]),
 'B9':  ('H4', [('b9', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B10': ('N', [('b10a', 'sync', G2, 2.63, dict(z0=1.0, z1=1.04)),                         # hasta que la mano se acerca al stick
               ('b10b', 'vid', HOST, None, dict(ss=12.50, z0=1.0, z1=1.03))]),             # el host escucha (boca quieta)
 'B11': ('H5', [('b11', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B12': ('T', [('b12', 'vid', f'{HF}/k_empuja_0.mp4', None, dict(ss=0.2, z0=1.0, z1=1.04))]),  # empuja la piedra al host (etiqueta original del clip, sin capa: pedido de Camilo)
 'B13': ('C', [('b13a', 'vid', f'{S}/hi_42130.mp4', 1.3, dict(ss=0.3, z0=1.0, z1=1.06)),
               ('b13b', 'still', f'{HF}/fixed/endcard_bano_real.png', None, dict(z0=1.0, z1=1.04))]),
}
EC_BOX = (259, 960, 801, 1600)   # producto + tapa en la tarjeta final (no se tapa)

TRIM = {'B4'}   # filas sin labios a la vista: las pausas internas de más de 0,3 s se recortan (brief: cero tiempo muerto)
MAXGAP = 0.18

def audio_plan(key, lk):
    """Tramos de audio de la fila: [(inicio_clip, fin_clip)] y palabras con tiempos en la línea de tiempo de la fila."""
    clip, a0, a1, pieces = LINES[lk]
    if key not in TRIM or len(pieces) < 2:
        return [(a0, a1)], words_of(lk)
    segs, words, t = [], [], 0.0
    for j, (text, s0, e0) in enumerate(pieces):
        st = a0 if j == 0 else s0 - MAXGAP / 2
        en = a1 if j == len(pieces) - 1 else e0 + MAXGAP / 2
        words += [(w, t + (x0 - st), t + (x1 - st)) for w, x0, x1 in B.word_times(text, s0, e0 - s0)]
        segs.append((st, en)); t += en - st
    return segs, words

def wav_segs(name, clip, segs, d):
    parts = []
    for k, (x0, x1) in enumerate(segs):
        wav(f'{name}_p{k}', clip, x0, x1 - x0); parts.append(f'{T}/{name}_p{k}.wav')
    if len(parts) == 1:
        os.replace(parts[0], f'{T}/{name}.wav'); return
    lst = f'{T}/{name}_parts.txt'; open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-af', f'apad=whole_dur={d:.3f}', '-t', f'{d:.3f}',
                    f'{T}/{name}.wav'], check=True)

def build_shots():
    shots, rowmeta = {}, {}
    for key, (lk, items) in ROWS.items():
        clip, a0, a1, _ = LINES[lk]
        segs, wds = audio_plan(key, lk); d = sum(b - a for a, b in segs)
        fixed = sum(x[3] for x in items if x[3]); rest = d - fixed
        lst, t = [], 0.0
        for name, kind, src, dd, o in items:
            dd = dd or rest
            o = dict(o)
            if o.get('ss') == 'a0': o['ss'] = a0 + t
            if kind == 'sync':
                sh = B.shot(T, name, src, dd, ss=a0 + t, **o)
            elif kind == 'still':
                sh = B.shot(T, name, src, dd, still=True, **o)
            else:
                sh = B.shot(T, name, src, dd, **o)
            if len(segs) == 1:
                wav(name, clip, a0 + t, dd)
            else:   # fila recortada: una sola toma (sin labios), audio armado por tramos
                wav_segs(name, clip, segs, dd)
            obst = None
            if name == 'b13b': obst = [EC_BOX]
            if any(k in src for k in ('ins_gota', 'ins_cal', 'k_grifo2', 'p_mesa', 'hi_42130', 'k_empuja')): obst = obst or []
            lst.append(sh + ((obst,) if obst is not None else ())); t += dd
        shots[key] = lst; rowmeta[key] = (d, wds)
    return shots, rowmeta

WH = f'{AU}/sfx_1489.mp3'
def cfg_for(meta):
    def row(key, **kw):
        d, wd = meta[key]
        return dict(key=key, clip_audio=True, dur=d, words=wd, line=' '.join(w for w, _, _ in wd), **kw)
    hooks = {
        'HA': dict(row('HA', subs=False, text=('“La piedra no sirve”:', '¿mito?'),
                       extras=[dict(type='stamp', text='MITO', size=70, angle=-12, x=812, y=655, t0=0.06, t1=meta['HA'][0])]),
                   ),
        'HB': dict(row('HB', subs=True, text=('Lo que nadie explica', 'del alumbre'),
                       extras=[dict(type='text', text='?', size=230, color=(255, 214, 0), stroke=12, stroke_color=(16, 42, 67),
                                    x=300, y=770, t0=0.1, t1=meta['HB'][0])])),
    }
    for h in hooks.values():
        h.pop('key')
    body = [row('B1'), row('B2'), row('B3', icon='👀'), row('B4', sfx=[(-0.1, WH, 0.18)]), row('B5', sfx=[(-0.1, WH, 0.18)]),
            row('B6'), row('B7', sfx=[(0.8, f'{AU}/splash_1311.mp3', 0.25)]), row('B8', sfx=[(-0.1, WH, 0.18)]), row('B9'), row('B10'),
            row('B11'), row('B12'), row('B13', sfx=[(-0.1, WH, 0.18)])]
    return dict(id='GEO_MOFU_A1_05', fmt='PODCAST', version=5, tmp=T, out_dir=A, vo_dir=T, min_face=50, hook_text_until=3.0,
                hook_slots=[360, 420, 470, 560, 700, 860, 1000], ai_label=True, cut_sfx=True, cut_sfx_vol=0.10, music_vol=0.07,
                hooks=hooks, body=body,
                cta=dict(row='B13', l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue'),   # + 'Pago contraentrega · Envío gratis' (brief)
                sfx={'HA': [(0.02, f'{AU}/sfx_2357.mp3', 0.6)]})

if __name__ == '__main__':
    shots, meta = build_shots()
    cfg = cfg_for(meta)
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
