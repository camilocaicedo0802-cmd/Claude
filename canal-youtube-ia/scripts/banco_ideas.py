"""Puntuación del banco de ideas (fase 8).

Las puntuaciones (1 a 5) son juicios a partir de la evidencia citada en la
columna `evidencia_demanda` (vidIQ y autocompletado de YouTube de la fase 3).
Total = suma(puntuación x peso) / 5, sobre 100.

Uso: python3 scripts/banco_ideas.py  ->  datos/banco_ideas.csv
"""
import csv
from pathlib import Path

PESOS = {
    "demanda": 20,
    "curiosidad": 15,
    "encaje_promesa": 15,
    "evidencia_fuentes": 15,
    "diferenciacion": 10,
    "apta_anunciantes": 10,
    "shorts_serie": 5,
    "costo_bajo": 10,
}

# (id, pilar, tema, keyword principal, evidencia de demanda, puntuaciones en el orden de PESOS)
IDEAS = [
    ("I01", "P1", "La verdadera historia de La Llorona", "la verdadera historia de la llorona",
     "Autocompletado MX/CO/AR; 'mitos y leyendas' 53.300 (comp. 42); 'leyendas mexicanas' 22.300 (+125 %)",
     (5, 5, 5, 4, 3, 3, 5, 4)),
    ("I02", "P2", "¿Por qué Colombia se llama Colombia?", "historia de colombia",
     "'historia de colombia' 40.400 (comp. 46, +142 %); la pregunta exacta sin medir",
     (4, 4, 4, 5, 4, 5, 4, 4)),
    ("I03", "P3", "Así vivías si nacías en Tenochtitlan", "como vivian los aztecas",
     "'como vivian los aztecas' 4.500 (comp. 40); 'tenochtitlan' 21.500; 'los aztecas' 24.200 (+161 %)",
     (4, 3, 3, 5, 3, 4, 4, 2)),
    ("I04", "P1", "El Dorado: lo que sí existió", "el dorado leyenda",
     "Sin medir (pendiente de vidIQ en noviembre)",
     (3, 5, 5, 5, 3, 5, 4, 3)),
    ("I05", "P2", "¿De verdad unos cientos de españoles conquistaron a los mexicas?", "conquista de mexico",
     "'hernan cortes' 26.200 (comp. 59); autocompletado 'porque los españoles conquistaron mexico'",
     (4, 5, 5, 5, 3, 3, 4, 2)),
    ("I06", "P4", "Una leyenda de cada país de Latinoamérica", "leyendas de cada pais",
     "Autocompletado 'leyendas de cada país' (+ 'de latam', Perú, Honduras, el Silbón)",
     (4, 4, 3, 3, 3, 3, 5, 2)),
    ("I07", "P1", "El chupacabras: cómo nació un monstruo moderno", "la leyenda del chupacabras",
     "Autocompletado MX/CO 'la leyenda del chupacabras'",
     (4, 4, 5, 4, 3, 4, 5, 4)),
    ("I08", "P1", "Las momias de Guanajuato: la historia real", "momias de guanajuato",
     "Autocompletado MX/CO/AR 'la leyenda de las momias de guanajuato'",
     (4, 5, 4, 4, 3, 2, 4, 3)),
    ("I09", "P2", "¿Por qué la capital de México está sobre un lago?", "historia de mexico",
     "'historia de mexico' 58.900 (comp. 60, +141 %); la pregunta exacta sin medir",
     (4, 4, 3, 5, 3, 5, 4, 3)),
    ("I10", "P2", "¿Por qué Panamá dejó de ser parte de Colombia?", "historia de colombia",
     "'historia de colombia' 40.400; la pregunta exacta sin medir",
     (3, 5, 4, 5, 3, 5, 4, 3)),
    ("I11", "P1", "El Silbón: de dónde sale la leyenda", "la leyenda del silbon",
     "Autocompletado CO 'la leyenda del silbón'; 'leyendas de cada país el silbón'",
     (3, 4, 3, 2, 3, 3, 4, 4)),
    ("I12", "P1", "La Patasola, el Mohán y la Madremonte", "leyendas de colombia",
     "Autocompletado 'leyendas de colombia la patasola'",
     (3, 3, 3, 2, 3, 3, 5, 3)),
    ("I13", "P2", "¿Por qué los incas no escribían? (los quipus)", "los incas",
     "Autocompletado 'los incas' (mezclado con música y 'para niños')",
     (3, 4, 4, 4, 3, 5, 4, 3)),
    ("I14", "P3", "Así vivías en la Nueva España", "como era la vida en la nueva españa",
     "Autocompletado MX 'como era la vida en la nueva españa'",
     (3, 3, 3, 4, 3, 4, 3, 3)),
    ("I15", "P1", "La Nahuala", "la leyenda de la nahuala",
     "Autocompletado MX/CO/AR, pero la intención es la película animada de 2007",
     (4, 3, 2, 2, 2, 3, 3, 3)),
    ("I16", "P1", "El Charro Negro", "la leyenda del charro negro",
     "Autocompletado MX/CO/AR, pero dominado por la película animada de 2018",
     (4, 3, 2, 2, 2, 3, 3, 3)),
]


def total(puntos):
    return round(sum(p * w for p, w in zip(puntos, PESOS.values())) / 5, 1)


def decision(t):
    if t >= 75:
        return "producir pronto"
    if t >= 60:
        return "banco"
    return "reformular o descartar"


def main():
    salida = Path(__file__).resolve().parent.parent / "datos" / "banco_ideas.csv"
    filas = []
    for id_, pilar, tema, kw, evid, puntos in IDEAS:
        t = total(puntos)
        filas.append([id_, pilar, tema, kw, evid, *puntos, t, decision(t)])
    filas.sort(key=lambda f: -f[-2])
    with salida.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "pilar", "tema", "keyword_principal", "evidencia_demanda",
                    *PESOS.keys(), "total_100", "decision"])
        w.writerows(filas)
    for f in filas:
        print(f"{f[0]} {f[1]} {f[-2]:5} {f[-1]:24} {f[2]}")


if __name__ == "__main__":
    main()
