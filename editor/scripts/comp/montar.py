"""Vídeos complementarios (preparación del abdomen, preparación de las piernas, cómo funciona el producto): monta la
toma de apoyo siguiendo la voz en off y detecta la cabeza.

Uso: python -I scripts/comp/montar.py <abdomen|piernas|producto> <carpeta del crudo> <modelo_yunet.onnx> [--solo-caras]
     <carpeta del crudo> (crudo/comp_a) contiene crudo.mp4 (el crudo de 20 min, 59,94 fps HEVC 10 bits),
     crudo_0_6.mp4 (sus primeros 6 min sin recodificar) y crudo_30.mp4 (esos 6 min a 30 fps CFR, sin audio).

Cada entrada del PLAN es (frase de la voz en off, toma). La toma empieza cuando se dice la frase y dura hasta la
siguiente. Claves de la toma:
- "src": segundo de crudo_30.mp4 (masaje manual: abdomen 0–3:20, piernas 3:30–6:00).
- "orig": segundo del crudo completo (b-roll del equipo después de los 6 min).
- "vel" < 1: cámara lenta desde el original a 60 fps (fluida); > 1: timelapse ("durante uno o dos minutos").
- "congela": fotograma congelado (pizarra).
Reglas (estilo.md §10.21–24): solo tramos sin conversación (transcripción del audio del crudo en
scripts/comp/transcripcion_crudo_a*.json), con la mirada en su cuerpo, la acción que dice la voz, y reencuadre para que
el borde derecho no deje ver el cuarto de al lado.
Salidas: public/comp_<vídeo>/apoyo.mp4 y su secuencia de JPEG public/comp_<vídeo>/fotogramas/00000.jpg… (la que usa
Remotion: el Chromium del entorno no decodifica H.264), src/comp_<vídeo>/data/clips.json y caras.json.
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
# Recorte 960×1707 desde (120, ENCUADRE_Y), escalado ×1,125 a 1080×1920: deja fuera la hoja impresa que hay sobre la
# mesa de la izquierda y acerca un poco a la persona (la cámara está más lejos que en el día 9). Por la derecha este
# crudo solo muestra la cortina, el banco y la pared.
ENCUADRE_REC = (120, 160, 960)  # (x, y, ancho) del recorte 9:16; una toma puede llevar el suyo en "rec"


def encuadre(rec) -> str:
    x, y, w = rec
    return f"crop={w}:{round(w * 16 / 9) // 2 * 2}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1"

PLAN: dict[str, list] = {
    # Masaje manual del abdomen (0–3:20 del crudo) y el equipo sobre el abdomen (14:20–16:30) para "rutina de Luma
    # Body". Fuera 0–17, 18,5–27, 50,8–53,6, 54–58, 60, 65–75, 133–160 y 189,5–198 s (habla o mira a cámara).
    "abdomen": [
        ("ahora", {"src": 86.0}),  # (debajo de la tarjeta) círculos alrededor del ombligo
        ("antes de comenzar", {"orig": 951.6}),  # el Luma Body sobre el abdomen: "nuestra rutina de Luma Body"
        ("vamos a preparar suavemente", {"src": 165.0}),  # masaje manual
        ("aplica", {"src": 199.0}),  # se sirve el aceite en la palma
        ("y frotalas", {"src": 251.3}),  # se frota las manos
        ("distribuirlo", {"src": 297.9, "vel": 0.5}),  # cámara lenta: frota el aceite entre las manos ("calentarlo")
        ("ahora ubica", {"src": 112.0}),  # las manos bajan a la parte baja del abdomen, junto a la ingle
        ("y realiza movimientos", {"src": 76.0}),  # círculos suaves en la parte baja
        ("deslizando", {"src": 107.4}),  # de los costados hacia el frente
        ("no necesitas", {"src": 126.0}),  # masaje lento, presión ligera
        ("despues lleva", {"src": 80.0}),  # las manos suben al abdomen: círculos amplios
        ("alrededor", {"src": 99.0, "congela": True}),  # congelado (pizarra): ombligo a la vista
        ("acompana", {"src": 100.0}),  # círculos lentos alrededor del ombligo (respiración)
        ("repite", {"src": 162.0, "vel": 3.0}),  # timelapse ×3: "durante uno o dos minutos… suficiente deslizamiento"
        ("continua", {"orig": 973.0}),  # el Luma Body sobre el abdomen: "continúa con tu rutina"
    ],
    # Masaje manual de las piernas (3:20–6:00, el pie sobre el banco) y el equipo en la pantorrilla (7:20–7:40).
    # Fuera 208,4–209,5, 216–234, 239–245 (incluido el bote de aceite enseñado a cámara), 282–284, 315–318 y 359–372 s.
    "piernas": [
        ("ahora", {"src": 322.0}),  # (debajo de la tarjeta) el pie en el banco, masaje desde el tobillo
        ("antes de utilizar", {"orig": 450.0}),  # el Luma Body en la pantorrilla
        ("prepara ambas", {"src": 263.2}),  # masaje manual con el pie en el banco
        ("comienza", {"src": 247.6}),  # se sirve el aceite en la palma
        # (aquí la cámara estaba más a la izquierda: recorte propio para dejar fuera la hoja impresa de la mesa)
        ("desde la pantorrilla", {"src": 205.4, "rec": (270, 100, 810)}),  # extiende el aceite por la pantorrilla
        ("y distribuyelo", {"src": 272.0}),  # las manos suben desde el tobillo
        ("desde encima del tobillo", {"src": 337.0}),  # del tobillo hacia la rodilla
        ("hasta llegar", {"src": 339.0, "congela": True}),  # congelado (pizarra): tobillo → antes de la rodilla
        ("al llegar", {"src": 302.0}),  # círculos suaves en la rodilla
        ("sin presionar", {"src": 345.5}),  # círculos alrededor de la rodilla, sin presionar
        ("luego", {"src": 340.4, "vel": 0.65}),  # de encima de la rodilla hacia el muslo
        ("deslizando", {"src": 310.0, "vel": 0.6}),  # cámara lenta: las manos suben por el muslo
        ("cuando te acerques", {"src": 334.6}),  # las manos llegan arriba del muslo
        ("disminuye", {"src": 336.0, "congela": True}),  # congelado (pizarra): termina antes de la ingle
        ("repite", {"src": 319.0, "vel": 3.0}),  # timelapse ×3: "durante aproximadamente 1 o 2 minutos" (cabeza a la izquierda)
        ("recuerda", {"src": 348.0}),  # masaje suave
        ("no necesitas", {"src": 352.0}),
        ("antes de comenzar", {"orig": 453.0}),  # el Luma Body en la pantorrilla: "tu rutina con Luma Body"
    ],
    "producto": [],
}


def trozo(carpeta: Path, toma: dict, frames: int, dst: Path) -> None:
    comunes = ["-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15",
               "-pix_fmt", "yuv420p", "-r", str(FPS), str(dst)]
    encuadre = globals()["encuadre"](toma.get("rec", ENCUADRE_REC))
    vel = toma.get("vel", 1.0)
    if vel > 1:
        fuente, s = carpeta / "crudo_30.mp4", toma["src"]
        filtro = f"setpts=(PTS-STARTPTS)/{vel},fps={FPS},{encuadre}"
    elif "orig" in toma:
        fuente, s = carpeta / "crudo.mp4", toma["orig"]
        filtro = f"setpts=(PTS-STARTPTS)/{vel},fps={FPS},{encuadre}"
    elif vel < 1:
        fuente, s = carpeta / "crudo_0_6.mp4", toma["src"]
        filtro = f"setpts=(PTS-STARTPTS)/{vel},fps={FPS},{encuadre}"
    else:
        fuente, s = carpeta / "crudo_30.mp4", toma["src"]
        filtro = encuadre
    if toma.get("congela"):
        filtro = f"trim=end_frame=1,{filtro},tpad=stop_mode=clone:stop={frames}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.4f}", "-i", str(fuente), "-map", "0:v:0", "-vf", filtro,
                    *comunes], check=True)


def main() -> None:
    video, carpeta = sys.argv[1], Path(sys.argv[2])
    solo_caras = "--solo-caras" in sys.argv
    dia = f"comp_{video}"
    edit = json.load(open(RAIZ / f"src/{dia}/data/edit.json"))
    words, total = edit["words"], edit["duration"] + HOLD
    anclas, t0 = [], 0.0
    for frase, toma in PLAN[video]:
        t = 0.0 if not anclas else buscar(words, frase, t0)
        anclas.append((round(t * FPS), toma, frase))
        t0 = t
    nfin = round(total * FPS)
    clips = []
    pub = RAIZ / f"public/{dia}"
    dst = pub / "apoyo.mp4"
    if solo_caras:
        return caras_de(dst, dia)
    pub.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        with open(lista, "w") as fl:
            for i, (f0, toma, frase) in enumerate(anclas):
                f1 = anclas[i + 1][0] if i + 1 < len(anclas) else nfin
                parte = Path(tmp) / f"c{i:02d}.mp4"
                trozo(carpeta, toma, f1 - f0, parte)
                fl.write(f"file '{parte}'\n")
                clips.append({"frase": frase, "outStart": f0 / FPS, "frames": f1 - f0, **toma})
                print(f"{f0 / FPS:6.2f}s  {(f1 - f0) / FPS:5.2f}s  {toma}  «{frase}»")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
                        "-movflags", "+faststart", str(dst)], check=True)
    (RAIZ / f"src/{dia}/data").mkdir(parents=True, exist_ok=True)
    json.dump(clips, open(RAIZ / f"src/{dia}/data/clips.json", "w"), ensure_ascii=False, indent=1)
    jpeg_y_caras(pub, dst, dia)


def jpeg_y_caras(pub: Path, dst: Path, dia: str) -> None:
    d = pub / "fotogramas"
    d.mkdir(exist_ok=True)
    for f in d.glob("*.jpg"):
        f.unlink()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(dst), "-an", "-q:v", "2", "-start_number", "0",
                    str(d / "%05d.jpg")], check=True)

    caras_de(dst, dia)


def caras_de(dst: Path, dia: str) -> None:
    # Cabeza cada 3 fotogramas: YuNet si se ve la cara; si no, la parte más alta de la silueta (la cortina es clara y
    # poco saturada; piel y pelo no)
    import cv2
    import numpy as np
    det = cv2.FaceDetectorYN.create(sys.argv[3], "", (540, 960), 0.55)
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
        # Inclinada, lo más alto de la silueta es la cabeza o la espalda: caja de 240 px centrada en el punto más alto
        # (con el ancho de las 30 filas de arriba la caja salía enorme y las columnas bajaban sobre la pierna)
        xs = np.nonzero((lab[top:top + 8] == i).any(axis=0))[0]
        cx = int(xs.mean()) * 4
        return [cx - 120, int(top) * 4 + 40, 240, 220]

    cap = cv2.VideoCapture(str(dst))
    caras, n, por_cara, por_sil = [], 0, 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if n % 3 == 0:
            _, res = det.detect(cv2.resize(fr, (540, 960)))
            if res is not None:  # la cara nunca baja de la mitad del cuadro (más abajo: rodilla, ombligo…)
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
    json.dump({"cada": 3, "caras": caras}, open(RAIZ / f"src/{dia}/data/caras.json", "w"))
    print(f"cabeza: {por_cara} por cara, {por_sil} por silueta, {len(caras) - por_cara - por_sil} sin datos (de {len(caras)})")


if __name__ == "__main__":
    main()
