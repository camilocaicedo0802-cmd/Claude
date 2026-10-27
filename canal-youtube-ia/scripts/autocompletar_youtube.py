import json, sys, time, urllib.parse, urllib.request, re
OUT = sys.argv[1]
SEEDS = {
 'historia_latam': ['historia de colombia', 'historia de mexico', 'historia de argentina', 'historia de america latina', 'la independencia de', 'simon bolivar', 'la conquista de', 'por que los españoles', 'los aztecas', 'los incas'],
 'por_que_historia': ['por que se acabo', 'por que dejaron de', 'por que desaparecio', 'por que ya no existen', 'por que perdio'],
 'verdad_detras': ['la verdadera historia de', 'el origen de', 'el origen oscuro de', 'la leyenda de', 'leyendas de', 'el significado de la cancion'],
 'vida_cotidiana': ['como vivian los', 'como era la vida en', 'asi era la vida', 'como se inventaron', 'quien invento'],
 'lugares_misterios': ['lugares prohibidos', 'lugares que no puedes visitar', 'misterios de', 'que pasaria si'],
 'guerra': ['segunda guerra mundial', 'la guerra de', 'la batalla de'],
}
COUNTRIES = ['MX', 'CO', 'AR']
res = {}
for group, seeds in SEEDS.items():
    for seed in seeds:
        for gl in COUNTRIES:
            q = urllib.parse.quote(seed)
            url = f"https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&hl=es&gl={gl}&q={q}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                raw = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'replace')
                m = re.search(r'\((.*)\)\s*$', raw, re.S)
                data = json.loads(m.group(1))
                sugg = [s[0] for s in data[1]]
            except Exception as e:
                sugg = ['ERROR ' + str(e)[:80]]
            res.setdefault(group, {}).setdefault(seed, {})[gl] = sugg
            time.sleep(1.5)
        print(group, seed, len(res[group][seed]['MX']), file=sys.stderr)
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
