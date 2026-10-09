"""Días 4 y 5: monta la toma de apoyo siguiendo la voz en off y detecta la cara en cada fotograma.

Uso: python -I scripts/rutinas/montar.py <dia4|dia5> <crudo30.mp4> [modelo_yunet.onnx]
     (crudo30.mp4 = el crudo de 20 min pasado a 30 fps CFR, sin audio)

PLAN: cada entrada es (frase de la voz en off, segundo del crudo). El fragmento empieza cuando se dice la frase y dura
hasta la frase siguiente, así la acción de la toma coincide con lo que se explica.
Salidas: public/<dia>/apoyo.mp4 (sin audio) y src/<dia>/data/caras.json (caja de la cara cada 3 fotogramas).
"""
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
FPS = 30
HOLD = 0.7

PLAN = {
    "dia4": [
        ("comenzamos", 195.0),  # levanta el Drena Oil y lo vierte
        ("aplica suficiente", 205.0),  # extiende el aceite por la pierna sobre el banco
        ("trabaja la pantorrilla", 430.0),  # Luma Body desde encima del tobillo hacia arriba
        ("antes de llegar", 449.0),
        ("realiza pasadas", 461.0),  # pasadas lentas y ascendentes
        ("cambia de pierna", 531.5),  # la otra pierna
        ("mantén una velocidad", 541.0),
        ("continúa con el muslo", 562.0),  # muslo por delante
        ("realiza líneas", 574.0),  # costado del muslo
        ("terminando antes", 588.0),
        ("divide la zona", 592.5),
        ("cambia al muslo", 711.5),  # el otro muslo, de perfil
        ("recuerda las líneas", 719.0),
        ("por el frente", 725.0),
        ("y recuerda debe", 730.5),
        ("si es que no", 622.5),  # coge el aceite y lo vierte en la mano
        ("finaliza con dos", 664.0),  # glúteo
        ("haz movimientos circulares", 676.0),
        ("pasadas ascendentes en", 689.0),
        ("combina", 697.0),
        ("con esto terminamos", 744.5),
        ("completaste", 747.5),
        ("apaga el dispositivo", 752.0),  # muestra el equipo a cámara
        ("realiza pases", 760.5),  # pases con las manos sobre la pierna
        ("hacia los ganglios", 816.0),  # manos hacia la ingle
    ],
    "dia5": [
        ("prepara la piel", 878.0),  # muestra el Drena Oil
        ("distribuye", 889.0),  # aceite por el abdomen
        ("los laterales", 902.0),
        ("recuerda mantener una", 930.5),  # muestra el equipo y sus botones
        ("realiza círculos", 939.0),
        ("luego vas a realizar", 966.0),
        ("arrastras y sueltas", 985.0),
        ("recuerda no sostener", 1002.0),
        ("ahora trabajarás", 1035.0),  # lateral, de perfil
        ("desde el costado", 1040.0),
        ("movimientos lentos", 1047.0),
        ("pasando por tu cintura", 1056.0),
        ("ahora vamos otros", 1076.5),  # el otro lateral
        ("arrastras desde", 1085.0),
        ("finalizamos", 1129.0),  # abdomen bajo
        ("recuerda mantener siempre", 1140.0),
        ("y al finalizar", 1207.5),  # masaje suave con las manos
        ("ahora ya completaste", 1157.5),
        ("recuerda que la constancia", 1160.5),
        ("apaga el equipo", 1166.0),
        ("retira el exceso", 1177.0),  # toalla
    ],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "".join(c for c in s if c.isalnum() or c == " ").strip()


def buscar(words, frase, desde=0.0):
    toks = norm(frase).split()
    for i in range(len(words) - len(toks) + 1):
        if words[i]["start"] < desde:
            continue
        if all(norm(words[i + k]["text"]) == t for k, t in enumerate(toks)):
            return words[i]["start"]
    raise SystemExit(f"Frase no encontrada: {frase}")


def main() -> None:
    dia, crudo = sys.argv[1], sys.argv[2]
    edit = json.load(open(RAIZ / f"src/{dia}/data/edit.json"))
    words, total = edit["words"], edit["duration"] + HOLD
    anclas, t0 = [], 0.0
    for frase, src in PLAN[dia]:
        t = 0.0 if not anclas else buscar(words, frase, t0)
        anclas.append((round(t * FPS), src, frase))
        t0 = t
    nfin = round(total * FPS)
    clips = []
    for i, (f0, src, frase) in enumerate(anclas):
        f1 = anclas[i + 1][0] if i + 1 < len(anclas) else nfin
        clips.append({"frase": frase, "outStart": f0 / FPS, "src": src, "frames": f1 - f0})
        print(f"{f0 / FPS:6.2f}s  {(f1 - f0) / FPS:5.2f}s  crudo {src:7.2f}–{src + (f1 - f0) / FPS:7.2f}  «{frase}»")
    # Recorte por fotograma exacto de cada fragmento y concatenación (sin audio)
    filtro = "".join(f"[0:v]trim=start_frame={round(c['src'] * FPS)}:end_frame={round(c['src'] * FPS) + c['frames']},setpts=PTS-STARTPTS[v{i}];" for i, c in enumerate(clips))
    filtro += "".join(f"[v{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=0[v]"
    dst = RAIZ / f"public/{dia}/apoyo.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", crudo, "-filter_complex", filtro, "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(dst)], check=True)
    json.dump(clips, open(RAIZ / f"src/{dia}/data/clips.json", "w"), ensure_ascii=False, indent=1)

    # Cara fotograma a fotograma (cada 3) con YuNet, para que ningún gráfico la toque
    if len(sys.argv) > 3:
        import cv2
        det = cv2.FaceDetectorYN.create(sys.argv[3], "", (540, 960), 0.6)
        cap = cv2.VideoCapture(str(dst))
        caras, n = [], 0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            if n % 3 == 0:
                _, res = det.detect(cv2.resize(fr, (540, 960)))
                if res is not None and len(res):
                    x, y, w, h = (float(v) * 2 for v in max(res, key=lambda r: r[14])[:4])
                    caras.append([n, round(x), round(y), round(w), round(h)])
                else:
                    caras.append([n, None, None, None, None])
            n += 1
        json.dump({"cada": 3, "caras": caras}, open(RAIZ / f"src/{dia}/data/caras.json", "w"))
        vistas = sum(1 for c in caras if c[1] is not None)
        print(f"caras: {vistas}/{len(caras)} muestras con cara")


if __name__ == "__main__":
    main()
