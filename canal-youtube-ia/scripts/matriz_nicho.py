"""Matriz ponderada de nichos (fase 5). Puntuaciones 1-5 (5 = mejor; en riesgos, 5 = menos riesgo).
Uso: python3 matriz_nicho.py > datos/matriz_nicho.csv
"""
import csv, sys
PESOS = {  # suman 100
    'demanda': 12, 'competencia': 10, 'diferenciacion': 12, 'viralidad': 8, 'evergreen': 8,
    'facilidad_constante': 8, 'costo_complejidad': 6, 'monetizacion': 10, 'audiencia_fiel': 8,
    'riesgo_politicas_copyright': 8, 'originalidad_con_ia': 5, 'expansion': 5}
OPC = {
 'O1 Historia de Latinoamérica desde preguntas y paradojas': dict(demanda=4, competencia=3, diferenciacion=4, viralidad=3, evergreen=5,
     facilidad_constante=3, costo_complejidad=3, monetizacion=4, audiencia_fiel=4, riesgo_politicas_copyright=4, originalidad_con_ia=4, expansion=3),
 'O2 Mitos y leyendas de Latinoamérica con su historia real': dict(demanda=4, competencia=3, diferenciacion=4, viralidad=4, evergreen=4,
     facilidad_constante=4, costo_complejidad=4, monetizacion=3, audiencia_fiel=3, riesgo_politicas_copyright=3, originalidad_con_ia=4, expansion=4),
 'O3 Híbrido: leyendas + preguntas de historia latinoamericana': dict(demanda=5, competencia=3, diferenciacion=4, viralidad=4, evergreen=5,
     facilidad_constante=3, costo_complejidad=3, monetizacion=4, audiencia_fiel=4, riesgo_politicas_copyright=4, originalidad_con_ia=4, expansion=4),
 'O4 Vida cotidiana e historia para dormir': dict(demanda=4, competencia=4, diferenciacion=2, viralidad=2, evergreen=4,
     facilidad_constante=2, costo_complejidad=2, monetizacion=3, audiencia_fiel=3, riesgo_politicas_copyright=2, originalidad_con_ia=2, expansion=3),
 'O5 Curiosidades globales en catálogo (tipo Paint)': dict(demanda=3, competencia=2, diferenciacion=2, viralidad=4, evergreen=3,
     facilidad_constante=4, costo_complejidad=4, monetizacion=3, audiencia_fiel=2, riesgo_politicas_copyright=3, originalidad_con_ia=3, expansion=4),
 'O6 Segunda Guerra Mundial e historia militar': dict(demanda=4, competencia=2, diferenciacion=2, viralidad=4, evergreen=4,
     facilidad_constante=3, costo_complejidad=3, monetizacion=2, audiencia_fiel=3, riesgo_politicas_copyright=2, originalidad_con_ia=3, expansion=3),
}
assert sum(PESOS.values()) == 100
w = csv.writer(sys.stdout)
w.writerow(['opcion'] + [f'{k} (peso {v})' for k, v in PESOS.items()] + ['total_sobre_100'])
res = []
for name, sc in OPC.items():
    total = sum(sc[k] * v for k, v in PESOS.items()) / 5  # 5 en todo = 100
    res.append((total, name)); w.writerow([name] + [sc[k] for k in PESOS] + [round(total, 1)])
for t, n in sorted(res, reverse=True): print(f"{t:5.1f}  {n}", file=sys.stderr)
