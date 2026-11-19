"""Recorte de alta precisión (BiRefNet) de las personas, solo en los fotogramas en los que
hay algo DETRÁS de ellas (palabras "behind" y tarjetas de b-roll). En el resto del segmento
el primer plano es transparente (no hace falta: no hay nada detrás).

MODNet perdía la parte superior del pelo sobre fondos oscuros; BiRefNet lo conserva.
Salida: public/clips/<id>_fg.webm (1080x1920, VP9 con alfa, CRF 12).
Uso: python3 -I prepare_matte_hq.py [ids...]
"""
import json
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, "/home/user/Claude/video-editor/scripts")
import matte_lib as M  # noqa: E402

ROOT = "/home/user/Claude/video-editor"
OW, OH = 1080, 1920
edl = json.load(open(f"{ROOT}/src/data/edl.json"))


def windows(clip):
    """Fotogramas DEL CLIP que necesitan recorte (con 3 de margen): los de todas las tomas que
    salen de ese clip y tienen algo detrás de la persona (palabras "behind" o tarjetas)."""
    need = set()
    spans = [(h["bFrom"], h["to"]) for h in edl["highlights"] if h["behind"]]
    spans += [(c["from_"], c["to"]) for c in edl["cards"]]
    for seg in edl["segments"]:
        if seg["clip"] != clip:
            continue
        a0, a1 = seg["from_"], seg["from_"] + seg["dur"]
        for s, e in spans:
            for f in range(max(s - 3, a0), min(e + 3, a1)):
                need.add(f - a0 + seg["clipStart"])
    return need


def main():
    only = set(sys.argv[1:])
    for clip in dict.fromkeys(s["clip"] for s in edl["segments"]):
        if only and clip not in only:
            continue
        need = windows(clip)
        mp4 = f"{ROOT}/public/clips/{clip}.mp4"
        out = f"{ROOT}/public/clips/{clip}_fg.webm"
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={OW}:{OH}:flags=lanczos",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{OW}x{OH}",
                                "-r", "30", "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0",
                                "-crf", "12", "-deadline", "good", "-cpu-used", "2", "-row-mt", "1",
                                "-auto-alt-ref", "0", out], stdin=subprocess.PIPE)
        n, prev, t0 = 0, None, time.time()
        while True:
            buf = dec.stdout.read(OW * OH * 3)
            if len(buf) < OW * OH * 3:
                break
            frame = np.frombuffer(buf, np.uint8).reshape(OH, OW, 3)
            if n in need:
                a = M.birefnet(frame.astype(np.float32) / 255, "birefnet/lite.onnx")
                # suavizado temporal ligero (evita que el borde tiemble) solo entre fotogramas seguidos
                if prev is not None and (n - 1) in need:
                    a = 0.7 * a + 0.3 * prev
                prev = a
                alpha = (np.clip(a, 0, 1) * 255).astype(np.uint8)
            else:
                alpha = np.zeros((OH, OW), np.uint8)
                prev = None
            enc.stdin.write(np.dstack([frame, alpha]).tobytes())
            n += 1
        enc.stdin.close()
        enc.wait()
        dec.wait()
        print(f"ok {clip}: {n} fotogramas, {len(need)} recortados con BiRefNet en {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
