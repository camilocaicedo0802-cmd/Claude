#!/usr/bin/env python3
"""Guarda / recupera los enlaces de lo generado en Higgsfield, para poder hacer correcciones (v2, v3) en otro chat.
uso: assets.py save <carpeta_hf> <assets.json> nombre1 nombre2 ...   (lee <nombre>.status.json y <nombre>.body.json)
     assets.py fetch <assets.json> <carpeta_hf>                        (vuelve a descargar <nombre>_0.ext)"""
import sys, json, os, subprocess
cmd = sys.argv[1]
if cmd == 'save':
    hf, out, names = sys.argv[2], sys.argv[3], sys.argv[4:]
    data = json.load(open(out)) if os.path.exists(out) else {}
    for n in names:
        st = json.load(open(f'{hf}/{n}.status.json'))
        urls = ([st['video']['url']] if st.get('video') else []) + [x['url'] for x in st.get('images') or []] + \
               [x['url'] for x in st.get('videos') or []]
        body = json.load(open(f'{hf}/{n}.body.json')) if os.path.exists(f'{hf}/{n}.body.json') else None
        data[n] = dict(urls=urls, body=body)
    json.dump(data, open(out, 'w'), indent=1, ensure_ascii=False)
    print('guardados', len(names), '->', out)
elif cmd == 'fetch':
    src, hf = sys.argv[2], sys.argv[3]
    os.makedirs(hf, exist_ok=True)
    for n, v in json.load(open(src)).items():
        for i, u in enumerate(v['urls']):
            ext = u.split('?')[0].rsplit('.', 1)[-1][:4]
            dst = f'{hf}/{n}_{i}.{ext}'
            if not os.path.exists(dst):
                subprocess.run(['curl', '-sSL', '--max-time', '300', '-o', dst, u], check=True); print(dst)
