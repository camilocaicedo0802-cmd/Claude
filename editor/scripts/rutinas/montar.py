"""Días 4, 5 y 6: monta la toma de apoyo siguiendo la voz en off y detecta la cara en cada fotograma.

Uso: python -I scripts/rutinas/montar.py <dia4|dia5|dia6> <crudo30.mp4> [modelo_yunet.onnx]
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
    # Día 6 (crudo propio de 9 min): fuera los momentos en que mira a cámara o habla con quien graba
    # (195, 246–249, 267, 321, 345, 411, 414, 420, 469–472 s) y el cambio de banco (366–369 s).
    "dia6": [
        ("prepara la piel", 6.0),  # se frota el aceite en las manos
        ("aplica aceite", 15.0),  # lo extiende por los muslos
        ("hoy nos", 27.0),
        ("comenzamos", 88.5),  # coge el equipo
        ("desliza desde", 99.0),  # muslo derecho: desde encima de la rodilla hacia arriba
        ("trabaja por líneas", 126.0),
        ("continúa durante", 219.0),  # círculos amplios en el muslo derecho
        ("sin detener", 252.0),
        ("haz círculos", 230.0),
        ("recuerda verificar", 205.5),  # mira el equipo y baja la intensidad
        ("ahora vamos a repetir", 270.0),  # muslo izquierdo: barridos
        ("deslizas", 282.0),
        ("y por otros", 324.0),  # pierna sobre el banco: círculos
        ("movimientos amplios", 348.0),
        ("para finalizar", 415.5),  # glúteo derecho (antes y después mira a cámara)
        ("con dos minutos", 432.0),
        ("el masaje", 423.0),
        ("trabaja dos minutos", 444.0),  # glúteo izquierdo
        ("barridos de abajo", 453.0),
        ("terminamos", 465.0),  # de espaldas y se gira (después habla a cámara)
        ("una mayor", 520.0),  # masaje con las manos
        ("así que prioriza", 527.5),
        ("la constancia", 539.8),
    ],
}


# Segundos del crudo con el fondo vacío (sale de cuadro), para localizar la silueta cuando la cara no se ve.
# El crudo del día 6 no tiene plano vacío: allí la silueta se saca por color.
FONDO = {
    "dia4": (842.0, 842.5, 843.0, 843.5, 844.0, 844.5),
    "dia5": (842.0, 842.5, 843.0, 843.5, 844.0, 844.5),
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
    # Cada fragmento se recorta por separado (búsqueda precisa + número exacto de fotogramas) y luego se concatenan
    # sin recodificar: con un único filter_complex de 25 trims ffmpeg se queda sin memoria.
    import tempfile
    dst = RAIZ / f"public/{dia}/apoyo.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        with open(lista, "w") as fl:
            for i, c in enumerate(clips):
                parte = Path(tmp) / f"c{i:02d}.mp4"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['src']:.4f}", "-i", crudo, "-frames:v", str(c["frames"]), "-an",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p", "-r", str(FPS), str(parte)], check=True)
                fl.write(f"file '{parte}'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", "-movflags", "+faststart", str(dst)], check=True)
    json.dump(clips, open(RAIZ / f"src/{dia}/data/clips.json", "w"), ensure_ascii=False, indent=1)

    # Cabeza fotograma a fotograma (cada 3), para que ningún gráfico la toque:
    #  1) YuNet cuando la cara se ve (de frente);
    #  2) si no (de perfil, agachada): la cámara está fija, así que se compara con el fondo vacío (FONDO) o, si no lo
    #     hay, con el color de la cortina; la parte más alta de la silueta es la cabeza.
    if len(sys.argv) > 3:
        import cv2
        import numpy as np
        det = cv2.FaceDetectorYN.create(sys.argv[3], "", (540, 960), 0.55)
        fondo = None
        if dia in FONDO:
            fondo_cap = cv2.VideoCapture(crudo)
            placas = []
            for seg in FONDO[dia]:
                fondo_cap.set(cv2.CAP_PROP_POS_MSEC, seg * 1000)
                ok, fr = fondo_cap.read()
                if ok:
                    placas.append(cv2.GaussianBlur(cv2.resize(fr, (270, 480)), (5, 5), 0).astype(np.int16))
            fondo = np.median(np.stack(placas), axis=0).astype(np.int16)
        k = np.ones((5, 5), np.uint8)

        def silueta(fr):
            peq = cv2.GaussianBlur(cv2.resize(fr, (270, 480)), (5, 5), 0)
            if fondo is not None:
                m = (np.abs(peq.astype(np.int16) - fondo).max(axis=2) > 28).astype(np.uint8)
            else:
                # Sin plano vacío (día 6): la cortina es clara y poco saturada; piel y pelo no
                hsv = cv2.cvtColor(peq, cv2.COLOR_BGR2HSV)
                m = ((hsv[..., 1] > 70) | (hsv[..., 2] < 110)).astype(np.uint8)
            m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
            n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
            if n < 2:
                return None
            i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            if st[i, cv2.CC_STAT_AREA] < 1500:
                return None
            top = st[i, cv2.CC_STAT_TOP]
            # ~220 px en 1080×1920: la cabeza. Sin plano vacío (día 6) basta ~120 px: con 220 entran hombros y brazos
            # cuando se agacha, y la caja sale el doble de ancha.
            banda = lab[top:top + (55 if fondo is not None else 30)] == i
            xs = np.nonzero(banda.any(axis=0))[0]
            x0, x1 = int(xs.min()) * 4, int(xs.max() + 1) * 4
            return [int(x0), int(top) * 4 + 60, int(x1 - x0), 200]  # misma forma que YuNet (la caja de YuNet empieza en la frente)

        cap = cv2.VideoCapture(str(dst))
        caras, n, por_cara, por_silueta = [], 0, 0, 0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            if n % 3 == 0:
                _, res = det.detect(cv2.resize(fr, (540, 960)))
                if res is not None and len(res):
                    x, y, w, h = (float(v) * 2 for v in max(res, key=lambda r: r[14])[:4])
                    caras.append([n, round(x), round(y), round(w), round(h)])
                    por_cara += 1
                else:
                    sil = silueta(fr)
                    caras.append([n, *sil] if sil else [n, None, None, None, None])
                    por_silueta += 1 if sil else 0
            n += 1
        json.dump({"cada": 3, "caras": caras}, open(RAIZ / f"src/{dia}/data/caras.json", "w"))
        print(f"cabeza: {por_cara} por cara, {por_silueta} por silueta, {len(caras) - por_cara - por_silueta} sin datos (de {len(caras)})")


if __name__ == "__main__":
    main()
