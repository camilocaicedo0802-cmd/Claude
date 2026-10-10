"""Día 7 "Piernas ligeras": monta la toma de apoyo de los DOS crudos siguiendo la voz en off y detecta la cabeza.

Uso: python -I scripts/dia7/montar.py <carpeta_crudos> <modelo_yunet.onnx>
     (la carpeta tiene crudo1.mp4 / crudo2.mp4 originales a 59,94 fps y crudo1_30.mp4 / crudo2_30.mp4 a 30 fps CFR)

Novedades frente a scripts/rutinas/montar.py (días 4–6), para que el día 7 no se vea igual:
- "vel": velocidad de la toma. < 1 = cámara lenta sacada del original a 60 fps (fluida); > 1 = timelapse.
- "split": pantalla partida, dos tomas apiladas (la mitad inferior de cada una, sin escalar: piernas, sin caras).
Salidas: public/dia7/apoyo.mp4, src/dia7/data/clips.json y src/dia7/data/caras.json.
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

# (frase de la voz en off, toma). Cada toma dura hasta la frase siguiente.
PLAN = [
    ("la rutina de hoy", {"src": (2, 154.8)}),  # sentada junto a las almohadas, sin prisa (cansada)
    ("pero no quieres", {"src": (2, 20.5)}),  # se levanta y coge el equipo: no abandona el hábito
    ("siéntate", {"src": (1, 145.5)}),  # sube la pierna a la cama
    ("prepara ambas", {"src": (1, 138.0)}),  # enseña el aceite a cámara y lo vierte
    ("selecciona", {"src": (2, 34.6)}),  # el equipo a cámara, con la pantalla
    ("aplica aceite", {"src": (1, 178.0)}),  # aceite en la pantorrilla
    ("trabajamos", {"src": (2, 47.0), "vel": 2.0}),  # timelapse: pasadas en la pantorrilla ("4 minutos")
    ("con movimientos", {"src": (1, 291.0), "vel": 0.6}),  # cámara lenta: "lentos y continuos"
    ("haz pasadas", {"src": (2, 56.5)}),  # desde el tobillo hacia arriba
    ("terminando", {"src": (2, 69.5)}),  # llega cerca de la rodilla
    ("después que", {"split": ((2, 50.0), (1, 300.0))}),  # "ambas pantorrillas": pantalla partida
    ("vas a continuar", {"src": (1, 363.0)}),  # muslo
    ("no necesitas", {"src": (2, 76.0), "vel": 3.0}),  # "rápido": la toma va a toda velocidad…
    ("necesitas mantener", {"src": (1, 381.0)}),  # …y vuelve al ritmo normal: "mantener el movimiento"
    ("recuerda no dejar", {"src": (1, 396.0)}),
    ("cuando termines", {"src": (2, 85.5)}),  # termina y deja el equipo
    ("puedes descansar", {"src": (2, 159.0), "vel": 0.8}),  # se tumba con las piernas sobre las almohadas
    ("incluso", {"src": (2, 163.5)}),
]


def trozo(carpeta: Path, toma: dict, frames: int, dst: Path) -> None:
    comunes = ["-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15",
               "-pix_fmt", "yuv420p", "-r", str(FPS), str(dst)]
    if "split" in toma:
        (fa, sa), (fb, sb) = toma["split"]
        dur = frames / FPS + 1
        filtro = ("[0:v]crop=1080:960:0:960,setpts=PTS-STARTPTS[a];[1:v]crop=1080:960:0:960,setpts=PTS-STARTPTS[b];"
                  "[a][b]vstack=inputs=2[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sa:.4f}", "-t", f"{dur:.3f}", "-i", str(carpeta / f"crudo{fa}_30.mp4"),
                        "-ss", f"{sb:.4f}", "-t", f"{dur:.3f}", "-i", str(carpeta / f"crudo{fb}_30.mp4"),
                        "-filter_complex", filtro, "-map", "[v]", *comunes], check=True)
        return
    f, s = toma["src"]
    vel = toma.get("vel", 1.0)
    # Cámara lenta desde el original a 60 fps (más fotogramas reales); el resto desde el crudo a 30 fps
    fuente = carpeta / (f"crudo{f}.mp4" if vel < 1 else f"crudo{f}_30.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.4f}", "-i", str(fuente), "-map", "0:v:0",
                    "-vf", f"setpts=(PTS-STARTPTS)/{vel},fps={FPS}", *comunes], check=True)


def main() -> None:
    carpeta = Path(sys.argv[1])
    edit = json.load(open(RAIZ / "src/dia7/data/edit.json"))
    words, total = edit["words"], edit["duration"] + HOLD
    anclas, t0 = [], 0.0
    for frase, toma in PLAN:
        t = 0.0 if not anclas else buscar(words, frase, t0)
        anclas.append((round(t * FPS), toma, frase))
        t0 = t
    nfin = round(total * FPS)
    clips = []
    dst = RAIZ / "public/dia7/apoyo.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        with open(lista, "w") as fl:
            for i, (f0, toma, frase) in enumerate(anclas):
                f1 = anclas[i + 1][0] if i + 1 < len(anclas) else nfin
                parte = Path(tmp) / f"c{i:02d}.mp4"
                trozo(carpeta, toma, f1 - f0, parte)
                fl.write(f"file '{parte}'\n")
                clips.append({"frase": frase, "outStart": f0 / FPS, "frames": f1 - f0, **{k: v for k, v in toma.items()}})
                print(f"{f0 / FPS:6.2f}s  {(f1 - f0) / FPS:5.2f}s  {toma}  «{frase}»")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
                        "-movflags", "+faststart", str(dst)], check=True)
    json.dump(clips, open(RAIZ / "src/dia7/data/clips.json", "w"), ensure_ascii=False, indent=1)

    # Cabeza cada 3 fotogramas: YuNet si se ve la cara; si no, la parte más alta de la silueta (la pared y la cama
    # son claras y poco saturadas; piel y pelo no). En la pantalla partida no hay caras: sin datos.
    import cv2
    import numpy as np
    det = cv2.FaceDetectorYN.create(sys.argv[2], "", (540, 960), 0.55)
    k = np.ones((5, 5), np.uint8)
    partidos = [(round(c["outStart"] * FPS), round(c["outStart"] * FPS) + c["frames"]) for c in clips if "split" in c]

    def silueta(fr):
        peq = cv2.GaussianBlur(cv2.resize(fr, (270, 480)), (5, 5), 0)
        hsv = cv2.cvtColor(peq, cv2.COLOR_BGR2HSV)
        m = ((hsv[..., 1] > 70) | (hsv[..., 2] < 90)).astype(np.uint8)
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
            if any(a <= n < b for a, b in partidos):
                caras.append([n, None, None, None, None])
            else:
                _, res = det.detect(cv2.resize(fr, (540, 960)))
                # En este crudo la cara nunca baja de la mitad del cuadro: lo que YuNet ve más abajo es un falso
                # positivo (p. ej. la cadera en un plano cercano)
                if res is not None:
                    res = [r for r in res if (r[1] + r[3] / 2) * 2 < 1150]
                if res is not None and len(res):
                    x, y, w, h = (float(v) * 2 for v in max(res, key=lambda r: r[14])[:4])
                    caras.append([n, round(x), round(y), round(w), round(h)])
                    por_cara += 1
                else:
                    sil = silueta(fr)
                    caras.append([n, *sil] if sil else [n, None, None, None, None])
                    por_sil += 1 if sil else 0
        n += 1
    json.dump({"cada": 3, "caras": caras}, open(RAIZ / "src/dia7/data/caras.json", "w"))
    print(f"cabeza: {por_cara} por cara, {por_sil} por silueta, {len(caras) - por_cara - por_sil} sin datos (de {len(caras)})")


if __name__ == "__main__":
    main()
