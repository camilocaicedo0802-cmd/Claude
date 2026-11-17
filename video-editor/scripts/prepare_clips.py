"""Prepara las tomas elegidas del bruto para Remotion.

Para cada segmento del guion:
  public/clips/<id>.mp4     1440x2560, 30 fps, gradación de color "E" (ver estilo.md),
                            voz procesada (AAC 48 kHz) y fundidos de 8 ms en los bordes.
  public/clips/<id>_fg.webm 1080x1920 VP9 con alfa: solo las personas (MODNet), para
                            poner textos/tarjetas detrás del sujeto.
Además public/clips/<id>.wav con la voz sola (para pistas de audio independientes).

Uso: python3 -I prepare_clips.py [ids...]   (sin ids = todos)
"""
import json
import os
import subprocess
import sys

import numpy as np
import onnxruntime as ort

ROOT = "/home/user/Claude/video-editor"
SRC = f"{ROOT}/assets_in/bruto/bruto.mp4"
OUT = f"{ROOT}/public/clips"
TMP = f"{ROOT}/analysis/tmp_clips"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

GRADE = ("curves=all='0/0 0.17/0.0 0.5/0.42 0.9/0.88 1/0.96',eq=saturation=1.45,"
         "colorbalance=rs=0.035:bs=-0.065:rm=0.008:bm=-0.008:rh=0.01:bh=-0.006")
VOICE = ("highpass=f=80,afftdn=nr=8:nf=-42,"
         "equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2.5,"
         "acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=3,"
         "alimiter=limit=0.89")

# id, inicio, fin (segundos del bruto), matte
SEGMENTS = [
    ("s1_hook", 1.70, 7.05, True),
    ("s2_editor", 9.95, 10.95, True),
    ("s3_cm", 16.85, 18.30, True),
    ("s4_meta", 22.95, 25.40, True),
    ("s5_sueldos", 90.20, 94.10, True),
    ("s6_marca", 122.55, 126.45, True),
    ("s7_vo", 178.05, 179.45, False),  # solo voz, va bajo el montaje de b-roll
    ("s8_cta", 196.35, 199.75, True),
]
VOICE_GAIN_DB = None  # se calcula para que la voz quede a -16 LUFS


def run(cmd):
    subprocess.run(cmd, check=True)


def voice_master():
    """Procesa todo el audio del bruto una vez (cadena de voz) y devuelve la ruta."""
    path = f"{TMP}/voz_procesada.wav"
    if not os.path.exists(path):
        run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-map", "0:a:0", "-ac", "1", "-ar", "48000",
             "-af", VOICE, path])
    return path


def loudness_of_segments(path):
    """LUFS integrados de la voz concatenando los tramos elegidos."""
    parts = []
    for _, a, b, _ in SEGMENTS:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", path,
                              "-f", "f32le", "-ac", "1", "-ar", "48000", "-"], capture_output=True).stdout
        parts.append(np.frombuffer(raw, np.float32))
    cat = f"{TMP}/voz_tramos.f32"
    np.concatenate(parts).tofile(cat)
    out = subprocess.run(["ffmpeg", "-v", "info", "-f", "f32le", "-ar", "48000", "-ac", "1", "-i", cat,
                          "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    line = [l for l in out.splitlines() if l.strip().startswith("I:")][-1]
    return float(line.split()[1])


def matte_segment(seg_id, mp4):
    sess = ort.InferenceSession(f"{ROOT}/.models/modnet/model.onnx", providers=["CPUExecutionProvider"])
    W, H = 512, 896  # entrada del modelo (múltiplos de 32, ~9:16)
    OW, OH = 1080, 1920
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={OW}:{OH}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                            "-s", f"{OW}x{OH}", "-r", "30", "-i", "-", "-c:v", "libvpx-vp9",
                            "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-deadline", "good",
                            "-cpu-used", "4", "-row-mt", "1", "-auto-alt-ref", "0",
                            f"{OUT}/{seg_id}_fg.webm"], stdin=subprocess.PIPE)
    n = 0
    prev = None
    while True:
        buf = dec.stdout.read(OW * OH * 3)
        if len(buf) < OW * OH * 3:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(OH, OW, 3)
        small = frame[::1, ::1]
        # redimensionado rápido a la entrada del modelo
        ys = (np.arange(H) * OH / H).astype(int)
        xs = (np.arange(W) * OW / W).astype(int)
        inp = small[ys][:, xs].astype(np.float32) / 255.0
        inp = ((inp - 0.5) / 0.5).transpose(2, 0, 1)[None]
        matte = sess.run(None, {"input": inp})[0][0, 0]
        # suavizado temporal ligero para evitar parpadeo del borde
        if prev is not None:
            matte = 0.75 * matte + 0.25 * prev
        prev = matte
        # escala la matte a 1080x1920 (bilineal separable)
        yi = np.linspace(0, H - 1, OH)
        xi = np.linspace(0, W - 1, OW)
        y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, H - 1); wy = (yi - y0)[:, None]
        x0 = np.floor(xi).astype(int); x1 = np.minimum(x0 + 1, W - 1); wx = (xi - x0)[None, :]
        m = (matte[y0][:, x0] * (1 - wx) + matte[y0][:, x1] * wx) * (1 - wy) + \
            (matte[y1][:, x0] * (1 - wx) + matte[y1][:, x1] * wx) * wy
        # endurece un poco el borde (curva) y lo pasa a 8 bits
        m = np.clip((m - 0.08) / 0.84, 0, 1)
        alpha = (m * 255).astype(np.uint8)
        rgba = np.dstack([frame, alpha])
        enc.stdin.write(rgba.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    return n


def main():
    only = set(sys.argv[1:])
    vpath = voice_master()
    lufs = loudness_of_segments(vpath)
    gain = -16.0 - lufs
    print(f"voz tramos: {lufs:.1f} LUFS -> ganancia {gain:+.1f} dB", flush=True)
    meta = {}
    for seg_id, a, b, need_matte in SEGMENTS:
        if only and seg_id not in only:
            continue
        dur = b - a
        wav = f"{OUT}/{seg_id}.wav"
        fade = f"volume={gain:.2f}dB,afade=t=in:d=0.008,afade=t=out:st={dur - 0.008:.3f}:d=0.008"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", vpath,
             "-af", fade, "-ar", "48000", "-ac", "1", wav])
        if seg_id == "s7_vo":
            meta[seg_id] = {"src_start": a, "src_end": b, "dur": dur}
            print("ok", seg_id, flush=True)
            continue
        mp4 = f"{OUT}/{seg_id}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", SRC, "-i", wav, "-t", f"{dur:.3f}",
             "-map", "0:v:0", "-map", "1:a:0",
             "-vf", f"scale=1440:2560:flags=lanczos,fps=30,{GRADE}",
             "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15",
             "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", mp4])
        frames = matte_segment(seg_id, mp4) if need_matte else None
        meta[seg_id] = {"src_start": a, "src_end": b, "dur": dur, "frames": frames}
        print("ok", seg_id, frames, flush=True)
    old = json.load(open(f"{OUT}/clips.json")) if os.path.exists(f"{OUT}/clips.json") else {}
    old.update(meta)
    json.dump(old, open(f"{OUT}/clips.json", "w"), indent=1)


if __name__ == "__main__":
    main()
