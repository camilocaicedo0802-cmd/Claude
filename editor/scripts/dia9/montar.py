"""Día 9 "Rutina integrada": monta la toma de apoyo siguiendo la voz en off, los dos mosaicos de zonas y la cabeza.

Uso: python -I scripts/dia9/montar.py <crudo_30.mp4> <modelo_yunet.onnx>
     (crudo_30.mp4 = el crudo de 10 min (59,94 fps, HEVC 10 bits) pasado a 30 fps CFR, sin audio)

Novedades frente a los días 4–8, para que el día 9 no se vea igual:
- "congela": la toma es un fotograma congelado (análisis tipo pizarra: líneas en el muslo, ombligo, codo y axila).
- "splitv": pantalla partida VERTICAL, dos momentos lado a lado (columna de 540 px de cada uno, sin escalar):
  "alternando ambos lados".
- Mosaicos 2×2 de las cuatro zonas (piernas, abdomen, glúteos, brazos), cada celda un recorte de 540×960 sin
  escalar: al empezar ("integraremos diferentes zonas en una sola rutina") y al cerrar ("para trabajar diferentes
  zonas"). Van en archivos aparte para que en Remotion las celdas se abran y dejen ver la toma de debajo.
Salidas: public/dia9/apoyo.mp4, public/dia9/mosaico_intro.mp4, public/dia9/mosaico_cierre.mp4,
         src/dia9/data/clips.json y src/dia9/data/caras.json.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rutinas"))
from montar import buscar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent
FPS = 30
HOLD = 0.7

# (frase de la voz en off, toma). Cada toma dura hasta la frase siguiente. Fuera los momentos en que mira a cámara
# o habla con quien graba (29–35, 57–62, 102, 130–137, 145–154, 162, 205, 233–235, 265, 341, 469 s).
PLAN = [
    ("hoy", {"src": 7.4}),  # debajo del mosaico; en "una sola rutina" está de pie frotándose el aceite en las manos
    ("aplica", {"src": 81.3}),  # primer plano: el aceite en la palma (sin cara)
    ("que vas", {"src": 16.0}),  # se aplica el aceite solo en las piernas
    ("empezamos", {"src": 37.0}),  # el equipo en la pantorrilla
    ("divide", {"src": 91.4, "congela": True}),  # primer plano de los muslos congelado: "divide la zona en líneas"
    ("movimientos ascendentes", {"src": 164.0}),  # de perfil: sube por la parte de atrás del muslo
    ("realiza líneas", {"src": 105.5}),  # desde la rodilla hacia arriba
    ("hacia arriba", {"src": 116.0}),  # parte alta del muslo (se reencuadra hacia la pierna)
    ("continúa", {"src": 196.3}),  # el equipo en el abdomen
    ("laterales", {"src": 476.0}),  # en el costado
    ("mantén", {"src": 470.3}),  # mira la pantalla del equipo: intensidad
    ("y evita", {"src": 479.5, "congela": True}),  # congelado de frente: el ombligo
    ("realiza círculos", {"src": 227.3}),  # abdomen bajo
    ("movimientos de", {"src": 217.0}),  # manos desde la espalda hacia la cintura
    ("hacia la cintura", {"src": 503.6}),  # el equipo baja hacia la ingle
    ("bajando", {"src": 88.4}),  # primer plano: la mano baja por el pliegue de la ingle
    ("trabaja", {"src": 240.2}),  # glúteos de espaldas
    ("con movimientos", {"src": 249.0}),
    ("barridos", {"src": 260.0}),
    ("haz círculos", {"splitv": ((243.0, 140), (256.4, 140))}),  # un lado y el otro, a la vez
    ("finaliza", {"src": 481.2}),  # brazo extendido con el equipo
    ("los brazos", {"src": 590.0}),  # solo con las manos
    ("o si", {"src": 501.0}),  # con el dispositivo, el otro brazo
    ("recuerda no", {"src": 488.0, "congela": True}),  # congelado: codo y axila
    ("y listo", {"src": 617.0}),
    ("para trabajar", {"src": 609.98}),  # (debajo del mosaico de cierre) se frota los brazos con calma
]

# Mosaicos: celdas en orden piernas · abdomen · glúteos · brazos, (segundo del crudo, x, y) de su recorte 540×960
MOSAICOS = {
    "intro": {"desde": "hoy", "hasta": ("sola", 0.9), "celdas": [(44.0, 230, 880), (196.5, 270, 520), (244.0, 150, 760), (482.0, 260, 150)]},
    "cierre": {"desde": "para trabajar", "hasta": ("sin", 0.6), "celdas": [(117.0, 250, 860), (229.0, 270, 560), (256.0, 130, 760), (502.0, 120, 150)]},
}


def trozo(crudo: str, toma: dict, frames: int, dst: Path) -> None:
    comunes = ["-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15",
               "-pix_fmt", "yuv420p", "-r", str(FPS), str(dst)]
    if "splitv" in toma:
        (sa, xa), (sb, xb) = toma["splitv"]
        dur = frames / FPS + 1
        filtro = (f"[0:v]crop=540:1920:{xa}:0,setpts=PTS-STARTPTS[a];[1:v]crop=540:1920:{xb}:0,setpts=PTS-STARTPTS[b];"
                  "[a][b]hstack=inputs=2[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sa:.4f}", "-t", f"{dur:.3f}", "-i", crudo,
                        "-ss", f"{sb:.4f}", "-t", f"{dur:.3f}", "-i", crudo, "-filter_complex", filtro, "-map", "[v]",
                        *comunes], check=True)
        return
    if toma.get("congela"):
        # Un solo fotograma repetido (tpad lo clona hasta completar la duración)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{toma['src']:.4f}", "-i", crudo, "-map", "0:v:0",
                        "-vf", f"trim=end_frame=1,tpad=stop_mode=clone:stop={frames}", *comunes], check=True)
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{toma['src']:.4f}", "-i", crudo, "-map", "0:v:0",
                    *comunes], check=True)


def mosaico(crudo: str, celdas, frames: int, dst: Path) -> None:
    entradas, filtro = [], ""
    for i, (s, x, y) in enumerate(celdas):
        entradas += ["-ss", f"{s:.4f}", "-t", f"{frames / FPS + 1:.3f}", "-i", crudo]
        filtro += f"[{i}:v]crop=540:960:{x}:{y},setpts=PTS-STARTPTS[c{i}];"
    filtro += "[c0][c1][c2][c3]xstack=inputs=4:layout=0_0|540_0|0_960|540_960[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", filtro, "-map", "[v]",
                    "-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(dst)], check=True)


def main() -> None:
    crudo = sys.argv[1]
    edit = json.load(open(RAIZ / "src/dia9/data/edit.json"))
    words, total = edit["words"], edit["duration"] + HOLD
    anclas, t0 = [], 0.0
    for frase, toma in PLAN:
        t = 0.0 if not anclas else buscar(words, frase, t0)
        anclas.append((round(t * FPS), toma, frase))
        t0 = t
    nfin = round(total * FPS)
    clips = []
    pub = RAIZ / "public/dia9"
    pub.mkdir(parents=True, exist_ok=True)
    dst = pub / "apoyo.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        with open(lista, "w") as fl:
            for i, (f0, toma, frase) in enumerate(anclas):
                f1 = anclas[i + 1][0] if i + 1 < len(anclas) else nfin
                parte = Path(tmp) / f"c{i:02d}.mp4"
                trozo(crudo, toma, f1 - f0, parte)
                fl.write(f"file '{parte}'\n")
                clips.append({"frase": frase, "outStart": f0 / FPS, "frames": f1 - f0, **toma})
                print(f"{f0 / FPS:6.2f}s  {(f1 - f0) / FPS:5.2f}s  {toma}  «{frase}»")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
                        "-movflags", "+faststart", str(dst)], check=True)
    (RAIZ / "src/dia9/data").mkdir(parents=True, exist_ok=True)
    json.dump(clips, open(RAIZ / "src/dia9/data/clips.json", "w"), ensure_ascii=False, indent=1)

    mosaicos = {}
    for nombre, m in MOSAICOS.items():
        a = buscar(words, m["desde"])
        frase, extra = m["hasta"]
        b = buscar(words, frase, a) + extra
        frames = round((b - a) * FPS)
        mosaico(crudo, m["celdas"], frames, pub / f"mosaico_{nombre}.mp4")
        mosaicos[nombre] = {"desde": round(a, 3), "hasta": round(a + frames / FPS, 3)}
        print(f"mosaico {nombre}: {a:.2f}–{a + frames / FPS:.2f}s")
    json.dump(mosaicos, open(RAIZ / "src/dia9/data/mosaicos.json", "w"), indent=1)

    # Cabeza cada 3 fotogramas: YuNet si se ve la cara; si no, la parte más alta de la silueta (la cortina es clara y
    # poco saturada; piel y pelo no). En la pantalla partida hay dos cabezas y en los primeros planos ninguna: allí
    # Dia9.tsx no coloca columnas.
    import cv2
    import numpy as np
    det = cv2.FaceDetectorYN.create(sys.argv[2], "", (540, 960), 0.55)
    k = np.ones((5, 5), np.uint8)

    def silueta(fr):
        peq = cv2.GaussianBlur(cv2.resize(fr, (270, 480)), (5, 5), 0)
        hsv = cv2.cvtColor(peq, cv2.COLOR_BGR2HSV)
        m = ((hsv[..., 1] > 70) | (hsv[..., 2] < 110)).astype(np.uint8)
        m[400:] = 0  # el suelo de madera y la mesa (y > 1600) no son la persona
        m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        if n < 2:
            return None
        i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        if st[i, cv2.CC_STAT_AREA] < 1500:
            return None
        top = st[i, cv2.CC_STAT_TOP]
        xs = np.nonzero((lab[top:top + 30] == i).any(axis=0))[0]
        x0, x1 = int(xs.min()) * 4, int(xs.max() + 1) * 4
        return [x0, int(top) * 4 + 60, x1 - x0, 200]

    cap = cv2.VideoCapture(str(dst))
    caras, n, por_cara, por_sil = [], 0, 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if n % 3 == 0:
            _, res = det.detect(cv2.resize(fr, (540, 960)))
            # La cara nunca baja de la mitad del cuadro: más abajo es un falso positivo (rodilla, ombligo…)
            if res is not None:
                res = [r for r in res if (r[1] + r[3] / 2) * 2 < 960]
            if res is not None and len(res):
                x, y, w, h = (float(v) * 2 for v in max(res, key=lambda r: r[14])[:4])
                caras.append([n, round(x), round(y), round(w), round(h)])
                por_cara += 1
            else:
                sil = silueta(fr)
                caras.append([n, *sil] if sil else [n, None, None, None, None])
                por_sil += 1 if sil else 0
        n += 1
    json.dump({"cada": 3, "caras": caras}, open(RAIZ / "src/dia9/data/caras.json", "w"))
    print(f"cabeza: {por_cara} por cara, {por_sil} por silueta, {len(caras) - por_cara - por_sil} sin datos (de {len(caras)})")


if __name__ == "__main__":
    main()
