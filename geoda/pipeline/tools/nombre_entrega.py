#!/usr/bin/env python3
"""Nombre de ENTREGA de un video (formato pedido por Camilo; desde el 26-nov con el FORMATO al final):
    '<Ángulo> GEO <ETAPA>-<A#>-<NN>-Hook <X>-<Formato>.mp4'
    ej. 'Axilas que lucen más parejas GEO TOFU-A2-04-Hook B-Podcast.mp4'
Si es una corrección de algo ya entregado se agrega ' v2', ' v3'… al final (opción --v N):
    'Axilas que lucen más parejas GEO TOFU-A2-04-Hook B-Podcast v2.mp4' 
Internamente el montaje sigue usando el nombre técnico (GEO_MOFU_A1_05_HA_PODCAST_v6.mp4); este script lo traduce.
uso: nombre_entrega.py GEO_MOFU_A1_05_HA_PODCAST_v6.mp4 [--v 2]
     nombre_entrega.py --copiar <carpeta_origen> <carpeta_destino>   (copia todos los .mp4 con el nombre de entrega)"""
import sys, re, os, shutil
ANGULOS = {
    'A1': 'La piedra no te falló', 'A2': 'Axilas que lucen más parejas', 'A3': 'La piedra de verdad, no un frasco',
    'A4': '1 piedra dura 1 año', 'A5': 'Ropa sin manchas', 'A6': 'Transición de 14 días', 'A7': 'Sigo sudando, pero no huelo',
    'A8': 'Antes creía que era cuento', 'A9': 'Hombres sin perfume, sin complicarse', 'A10': 'Calor, Costa y viaje',
    'A11': 'Primer desodorante del adolescente',
}
PAT = re.compile(r'GEO_(TOFU|MOFU|BOFU)_(A\d+)_(?:[A-Za-z0-9]+_)?(\d{2})_H([A-Z])_([A-Z]+)')
# códigos de formato del brief -> nombre legible al final del nombre de entrega (PODCAST_K2 -> PODCAST)
FORMATOS = {'UGC': 'UGC', 'DEMO': 'Demo', 'POV': 'POV', 'COMP': 'Comparación', 'MOTION': 'Motion graphics', 'TEST': 'Testimonio',
            'UNBOX': 'Unboxing', 'DIARIO': 'Diario 14 días', 'BASCULA': 'Báscula', 'PIXAR': 'Pixar', 'CLAY': 'Claymation',
            'PODCAST': 'Podcast', 'STREET': 'Street interview', 'FOUNDER': 'Founder'}

def nombre(tecnico, v=None):
    m = PAT.search(os.path.basename(tecnico))
    if not m:
        raise SystemExit(f'no reconozco el nombre: {tecnico}')
    etapa, ang, nn, hook, fmt = m.groups()
    n = f'{ANGULOS[ang]} GEO {etapa}-{ang}-{nn}-Hook {hook}-{FORMATOS.get(fmt, fmt.title())}'
    return n + (f' v{v}' if v and int(v) > 1 else '') + '.mp4'

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--copiar':
        src, dst = a[1], a[2]; os.makedirs(dst, exist_ok=True)
        for f in sorted(os.listdir(src)):
            if f.endswith('.mp4'):
                shutil.copy2(os.path.join(src, f), os.path.join(dst, nombre(f))); print(f, '->', nombre(f))
    else:
        v = a[a.index('--v') + 1] if '--v' in a else None
        print(nombre(a[0], v))
