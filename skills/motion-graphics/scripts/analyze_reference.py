#!/usr/bin/env python3
"""
Analiza un vídeo de referencia y mide su GRAMÁTICA DE EDICIÓN (no solo su estética).

Salida en <outdir>:
  analysis.json        métricas completas (cortes, planos, cámara, color, texto, audio)
  analisis.md          resumen legible para escribir estilo.md
  frames_2fps/         fotogramas cada 0.5 s
  frames_cortes/       primer fotograma de cada plano
  contact_*.jpg        hojas de contactos (2 fps paginadas + una miniatura por plano)
  audio.wav            audio de la referencia
  ocr_timeline.json    (con --ocr) cajas de texto en el tiempo
  separado/            (con --separate) voz / resto (Demucs)
  transcripcion.json   (con --whisper) palabras con tiempos

Uso:
  python3 analyze_reference.py referencia.mp4 analisis_ref --ocr --separate --whisper small --lang es

Todas las medidas de tamaño se dan también "a escala 1080 de ancho" para trasladarlas a un proyecto 1080×1920.
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------------- utilidades
def sh(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"Fallo: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    num, den = (int(x) for x in v.get("avg_frame_rate", v["r_frame_rate"]).split("/"))
    fps = num / den if den else 30.0
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) in (90, 270):
        w, h = h, w
    return {
        "width": w,
        "height": h,
        "fps": round(fps, 3),
        "duration": float(d["format"]["duration"]),
        "aspect": f"{w}:{h}",
        "orientation": "vertical" if h > w else ("horizontal" if w > h else "cuadrado"),
        "has_audio": a is not None,
        "audio_sr": int(a["sample_rate"]) if a else None,
        "audio_channels": int(a["channels"]) if a else None,
    }


def read_frames(path, width, fps=None, gray=True):
    """Lee fotogramas reducidos como array numpy (N, h, w[, 3])."""
    info = probe(path)
    h = int(round(info["height"] * width / info["width"] / 2) * 2)
    vf = (f"fps={fps}," if fps else "") + f"scale={width}:{h}"
    pix = "gray" if gray else "rgb24"
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-f", "rawvideo", "-pix_fmt", pix, "-"], capture_output=True)
    ch = 1 if gray else 3
    n = len(r.stdout) // (width * h * ch)
    arr = np.frombuffer(r.stdout[: n * width * h * ch], dtype=np.uint8)
    return arr.reshape((n, h, width) if gray else (n, h, width, 3))


def mad(x):
    return float(np.median(np.abs(x - np.median(x)))) + 1e-9


# ----------------------------------------------------------------------------- cortes y planos
def detect_cuts(gray, fps, sensitivity=1.0):
    """Cortes duros por distancia de histograma + diferencia de píxeles, con umbral adaptativo.
    También marca transiciones suaves (cambio sostenido varios frames: fundidos, barridos, whips)."""
    n = len(gray)
    if n < 3:
        return [], [], np.zeros(0), np.zeros(0)
    hists = np.stack([np.histogram(f, bins=32, range=(0, 255))[0] / f.size for f in gray])
    hd = np.abs(np.diff(hists, axis=0)).sum(1)  # 0..2
    pd = np.abs(np.diff(gray.astype(np.int16), axis=0)).mean((1, 2)) / 255.0  # 0..1
    score = 0.6 * hd / 2 + 0.4 * pd * 4
    thr = max(0.08, np.median(score) + 9 * mad(score)) / sensitivity
    cuts = []
    for i in range(len(score)):
        lo, hi = max(0, i - 3), min(len(score), i + 4)
        if score[i] >= thr and score[i] == score[lo:hi].max():
            t = (i + 1) / fps
            if not cuts or t - cuts[-1]["t"] > 3 / fps:
                cuts.append({"t": round(t, 3), "score": round(float(score[i]), 3)})
    # transiciones suaves: ventana de 8 frames con cambio medio alto pero sin pico de corte
    soft = []
    win = max(4, int(fps * 0.25))
    sm = np.convolve(score, np.ones(win) / win, mode="same")
    sthr = max(0.03, np.median(score) + 4 * mad(score))
    i = 0
    while i < len(sm):
        if sm[i] > sthr:
            j = i
            while j < len(sm) and sm[j] > sthr:
                j += 1
            a, b = i / fps, j / fps
            if b - a >= 0.12 and not any(a - 0.1 <= c["t"] <= b + 0.1 for c in cuts):
                soft.append({"start": round(a, 3), "end": round(b, 3), "peak": round(float(score[i:j].max()), 3)})
            i = j
        else:
            i += 1
    return cuts, soft, score, pd


def shots_from_cuts(cuts, duration):
    bounds = [0.0] + [c["t"] for c in cuts] + [duration]
    return [{"i": k, "start": round(bounds[k], 3), "end": round(bounds[k + 1], 3), "dur": round(bounds[k + 1] - bounds[k], 3)} for k in range(len(bounds) - 1) if bounds[k + 1] - bounds[k] > 0.02]


# ----------------------------------------------------------------------------- cámara
_WIN = {}


def phase_shift(a, b):
    """Desplazamiento de b respecto de a con precisión subpíxel (ajuste parabólico del pico)."""
    h, w = a.shape
    if (h, w) not in _WIN:
        _WIN[(h, w)] = np.outer(np.hanning(h), np.hanning(w))
    win = _WIN[(h, w)]
    A = np.fft.fft2((a - a.mean()) * win)
    B = np.fft.fft2((b - b.mean()) * win)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(r), r.shape)

    def refine(m1, m0, p1):
        d = m1 - 2 * m0 + p1
        return 0.0 if abs(d) < 1e-9 else 0.5 * (m1 - p1) / d

    fx = x + refine(r[y, (x - 1) % w], r[y, x], r[y, (x + 1) % w])
    fy = y + refine(r[(y - 1) % h, x], r[y, x], r[(y + 1) % h, x])
    if fy > h / 2:
        fy -= h
    if fx > w / 2:
        fx -= w
    return float(-fx), float(-fy), float(r.max())


def camera_motion(gray, fps, scale_to_1080, step=3):
    """Desplazamiento global del contenido (px/s a escala 1080 de ancho) comparando el fotograma i con el i+step.
    Signo: dy < 0 = el contenido sube (la cámara baja / tilt down)."""
    g = gray.astype(np.float32)
    n = len(g)
    pans, conf = [], []
    for i in range(n - 1):
        j = min(n - 1, i + step)
        dx, dy, c = phase_shift(g[i], g[j])
        pans.append((dx * scale_to_1080 * fps / (j - i), dy * scale_to_1080 * fps / (j - i)))
        conf.append(c)
    return np.array(pans), np.array(conf)


def best_scale(a, b, scales=None):
    """Escala de b respecto de a (búsqueda en 31 escalas, robusta a desplazamientos)."""
    from scipy.ndimage import zoom as nzoom

    if scales is None:
        scales = np.geomspace(0.8, 1.25, 31)
    h, w = a.shape
    best = (0.0, 1.0)
    for sc in scales:
        z = nzoom(b, 1 / sc, order=1)
        zh, zw = z.shape
        if zh >= h:
            y0, x0 = (zh - h) // 2, (zw - w) // 2
            aa, bb = a, z[y0 : y0 + h, x0 : x0 + w]
        else:
            y0, x0 = (h - zh) // 2, (w - zw) // 2
            aa, bb = a[y0 : y0 + zh, x0 : x0 + zw], z
        if aa.shape != bb.shape or min(aa.shape) < 16:
            continue
        c = phase_shift(aa, bb)[2]
        if c > best[0]:
            best = (c, float(sc))
    return best[1], best[0]


def zoom_samples(gray, fps, dt=0.5, every=0.25, min_conf=0.15):
    """Muestras de zoom: (t, zoom_por_s) comparando fotogramas separados dt segundos. zoom_por_s = escala^(1/dt) − 1."""
    g = gray.astype(np.float32)
    out = []
    t = 0.0
    dur = len(g) / fps
    while t + dt < dur:
        i, j = int(t * fps), int((t + dt) * fps)
        sc, c = best_scale(g[i], g[j])
        if c >= min_conf:
            out.append((round(t + dt / 2, 2), round(sc ** (1 / dt) - 1, 4)))
        t += every
    return out


def classify_motion(p, zoom, diff):
    """Clasifica el movimiento de un plano. Velocidades en px/s a escala 1080; zoom en fracción de escala/s."""
    if len(p) == 0:
        return {"tipo": "estático", "vel_px_s_1080": 0.0, "direccion": "-", "zoom_por_s": 0.0, "jitter": 0.0, "cambio_medio": 0.0, "tiene_whip": False}
    dx, dy = float(np.median(p[:, 0])), float(np.median(p[:, 1]))
    speed = float(np.hypot(dx, dy))
    peak = float(np.percentile(np.hypot(p[:, 0], p[:, 1]), 95))
    jitter = float(np.median(np.abs(np.diff(p, axis=0)))) if len(p) > 3 else 0.0
    change = float(np.mean(diff)) if len(diff) else 0.0
    if abs(dx) > abs(dy):
        direc = "contenido →" if dx > 0 else "contenido ←"
    else:
        direc = "contenido ↓" if dy > 0 else "contenido ↑"
    if abs(zoom) > 0.03:
        kind = "zoom-in" if zoom > 0 else "zoom-out"
    elif speed > 600:
        kind = "barrido/whip"
    elif speed > 60:
        kind = "pan/tilt"
    elif speed > 8:
        kind = "deriva lenta"
    elif jitter > 40:
        kind = "cámara en mano"
    elif change > 0.02:
        kind = "animación interna (cámara fija)"
    else:
        kind = "estático"
    return {"tipo": kind, "vel_px_s_1080": round(speed, 1), "direccion": direc if speed > 8 else "-", "zoom_por_s": round(zoom, 4), "jitter": round(jitter, 1), "cambio_medio": round(change, 4), "tiene_whip": peak > 1200}


# ----------------------------------------------------------------------------- color
def kmeans(x, k=6, iters=12, seed=0):
    rng = np.random.default_rng(seed)
    c = x[rng.choice(len(x), k, replace=False)].astype(np.float32)
    for _ in range(iters):
        d = ((x[:, None, :] - c[None]) ** 2).sum(2)
        lab = d.argmin(1)
        for j in range(k):
            m = x[lab == j]
            if len(m):
                c[j] = m.mean(0)
    counts = np.bincount(lab, minlength=k)
    order = np.argsort(-counts)
    return c[order], counts[order] / counts.sum()


def hexc(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)


def color_stats(rgb):
    px = rgb.reshape(-1, 3).astype(np.float32)
    rng = np.random.default_rng(1)
    sample = px[rng.choice(len(px), min(len(px), 20000), replace=False)]
    cent, frac = kmeans(sample, k=6)
    mx = sample.max(1)
    mn = sample.min(1)
    sat = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
    lum = (0.2126 * sample[:, 0] + 0.7152 * sample[:, 1] + 0.0722 * sample[:, 2]) / 255
    return {
        "paleta": [{"hex": hexc(c), "peso": round(float(f), 3)} for c, f in zip(cent, frac)],
        "luminancia_media": round(float(lum.mean()), 3),
        "saturacion_media": round(float(sat.mean()), 3),
        "tema": "claro" if lum.mean() > 0.6 else ("oscuro" if lum.mean() < 0.35 else "medio"),
        "monocromo": bool(sat.mean() < 0.08),
    }


def grain_and_vignette(frame_rgb):
    g = frame_rgb.mean(2).astype(np.float32)
    h, w = g.shape
    lap = np.abs(4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])
    bs = 16
    blocks = []
    for y in range(0, h - bs - 2, bs):
        for x in range(0, w - bs - 2, bs):
            blk = g[y + 1 : y + bs + 1, x + 1 : x + bs + 1]
            blocks.append((blk.std(), lap[y : y + bs, x : x + bs].mean()))
    blocks.sort()
    flat = blocks[: max(1, len(blocks) // 10)]
    grain = float(np.mean([b[1] for b in flat]))
    cs = max(4, min(h, w) // 10)
    corners = np.median([g[:cs, :cs].mean(), g[:cs, -cs:].mean(), g[-cs:, :cs].mean(), g[-cs:, -cs:].mean()])
    mids = [g[:cs, w // 2 - cs // 2 : w // 2 + cs // 2].mean(), g[-cs:, w // 2 - cs // 2 : w // 2 + cs // 2].mean(), g[h // 2 - cs // 2 : h // 2 + cs // 2, :cs].mean(), g[h // 2 - cs // 2 : h // 2 + cs // 2, -cs:].mean()]
    edge = max(np.median(mids), 1e-6)
    return round(grain, 2), round(float(corners / edge), 3)


# ----------------------------------------------------------------------------- OCR (subtítulos / textos)
def ocr_timeline(video, info, step):
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("  [ocr] falta rapidocr-onnxruntime (pip install rapidocr-onnxruntime); se omite", file=sys.stderr)
        return None
    ocr = RapidOCR()
    W = 720
    frames = read_frames(video, W, fps=1 / step, gray=False)
    H = frames.shape[1]
    out = []
    for i, fr in enumerate(frames):
        res, _ = ocr(fr)
        boxes = []
        for r in res or []:
            pts, text, score = r[0], r[1], float(r[2])
            if score < 0.6 or not text.strip():
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            crop = fr[int(y0) : int(y1) + 1, int(x0) : int(x1) + 1].reshape(-1, 3).astype(np.float32)
            col = None
            if len(crop) > 20:
                L = crop.mean(1)
                thr = (L.min() + L.max()) / 2
                a, b = crop[L < thr], crop[L >= thr]
                ink, bg = (a, b) if len(a) < len(b) else (b, a)
                if len(ink) and len(bg):
                    col = {"texto": hexc(ink.mean(0)), "fondo": hexc(bg.mean(0)), "fondo_uniforme": bool(bg.std(0).mean() < 18)}
            boxes.append(
                {
                    "text": text,
                    "score": round(score, 2),
                    "x0": round(x0 / W, 3),
                    "x1": round(x1 / W, 3),
                    "y0": round(y0 / H, 3),
                    "y1": round(y1 / H, 3),
                    "alto_px_1080": round((y1 - y0) * 1080 / W, 1),
                    "color": col,
                }
            )
        out.append({"t": round(i * step, 2), "boxes": boxes})
    return out


def summarize_text(tl):
    if not tl:
        return None
    present = [f for f in tl if f["boxes"]]
    allb = [b for f in tl for b in f["boxes"]]
    if not allb:
        return {"texto_en_pantalla": "no detectado"}
    yc = np.array([(b["y0"] + b["y1"]) / 2 for b in allb])
    hs = np.array([b["alto_px_1080"] for b in allb])
    xc = np.array([(b["x0"] + b["x1"]) / 2 for b in allb])
    x0 = np.array([b["x0"] for b in allb])
    words = [len(b["text"].split()) for b in allb]
    letters = "".join(b["text"] for b in allb)
    up = sum(c.isupper() for c in letters) / max(1, sum(c.isalpha() for c in letters))
    if np.std(x0) < 0.04 and np.median(x0) < 0.3:
        align = "izquierda"
    elif abs(np.median(xc) - 0.5) < 0.06:
        align = "centrado"
    else:
        align = "mixto"
    # granularidad: seguir cada caja (misma línea y arranque) y ver si su texto crece o se sustituye
    grow = swap = 0
    prev_boxes = []
    for f in tl:
        for b in f["boxes"]:
            yc_b = (b["y0"] + b["y1"]) / 2
            same = [p for p in prev_boxes if abs((p["y0"] + p["y1"]) / 2 - yc_b) < 0.03 and abs(p["x0"] - b["x0"]) < 0.06]
            if not same:
                continue
            p = same[0]
            a_, b_ = p["text"].replace(" ", ""), b["text"].replace(" ", "")
            if a_ == b_:
                continue
            if len(b_) > len(a_) and (b_.startswith(a_[: max(1, len(a_) - 2)]) or a_[:3] == b_[:3]):
                grow += 1
            elif len(b_) >= 2:
                swap += 1
        prev_boxes = f["boxes"]
    # tamaños: ¿uno o dos niveles tipográficos?
    lh = np.log(hs)
    lo_c, hi_c = np.percentile(lh, 25), np.percentile(lh, 75)
    for _ in range(10):
        lab = np.abs(lh - lo_c) > np.abs(lh - hi_c)
        if lab.all() or (~lab).all():
            break
        lo_c, hi_c = lh[~lab].mean(), lh[lab].mean()
    ratio = float(np.exp(hi_c - lo_c))
    frac_hi = float(lab.mean()) if len(lh) else 0
    niveles = f"dos tamaños ≈ {np.exp(lo_c):.0f} px y {np.exp(hi_c):.0f} px (×{ratio:.1f})" if ratio > 1.6 and 0.15 < frac_hi < 0.85 else "un tamaño dominante"
    cols = [b["color"]["texto"] for b in allb if b.get("color")]
    boxed = [b["color"]["fondo_uniforme"] for b in allb if b.get("color")]
    bands = np.histogram(yc, bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0])[0]
    return {
        "texto_presente_%": round(100 * len(present) / len(tl), 1),
        "posicion_vertical_mediana_%": round(100 * float(np.median(yc)), 1),
        "posicion_vertical_rango_%": [round(100 * float(np.percentile(yc, 10)), 1), round(100 * float(np.percentile(yc, 90)), 1)],
        "franjas_verticales_(0-20,20-40,40-60,60-80,80-100%)": bands.tolist(),
        "alineacion": align,
        "alto_caja_px_1080_mediana": round(float(np.median(hs)), 1),
        "alto_caja_px_1080_max": round(float(np.max(hs)), 1),
        "niveles_tipograficos": niveles,
        "palabras_por_caja_mediana": float(np.median(words)),
        "palabras_por_caja_max": int(max(words)),
        "ratio_mayusculas": round(up, 2),
        "aparicion": ("acumulativa (crece palabra a palabra)" if grow >= swap else "mixta: parte crece y parte se sustituye (verifica en ocr_timeline.json)") if grow >= 0.3 * swap else "por bloques (se reemplaza)",
        "cambios_acumulativos": grow,
        "cambios_de_bloque": swap,
        "colores_texto_frecuentes": [c for c, _ in sorted(((c, cols.count(c)) for c in set(cols)), key=lambda x: -x[1])[:5]],
        "caja_de_fondo_probable_%": round(100 * float(np.mean(boxed)), 1) if boxed else None,
    }


# ----------------------------------------------------------------------------- audio
def loudness(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary") :]
    out = {}
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            out["lufs_integrado"] = float(line.split()[1])
        if line.startswith("LRA:"):
            out["lra"] = float(line.split()[1])
        if line.startswith("Peak:"):
            out["pico_real_dbfs"] = float(line.split()[1])
    return out


def audio_analysis(wav, cuts, separate_dir=None):
    try:
        import librosa
    except ImportError:
        return {"error": "falta librosa"}
    y, sr = librosa.load(wav, sr=22050, mono=True)
    hop = 220
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
    db = 20 * np.log10(rms + 1e-9)
    thr = np.percentile(db, 95) - 30
    t = np.arange(len(db)) * hop / sr
    sil, s0 = [], None
    for i, v in enumerate(db < thr):
        if v and s0 is None:
            s0 = i
        if not v and s0 is not None:
            if (i - s0) * hop / sr >= 0.2:
                sil.append([round(t[s0], 2), round(t[i], 2)])
            s0 = None
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(1)
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    res = {
        **loudness(wav),
        "silencios_>0.2s": sil,
        "tempo_bpm_estimado": round(float(np.atleast_1d(tempo)[0]), 1),
        "onsets_por_segundo": round(len(onsets) / (len(y) / sr), 2),
        "notas_dominantes": [names[i] for i in np.argsort(chroma)[::-1][:5]],
    }
    if separate_dir and os.path.exists(os.path.join(separate_dir, "vocals.wav")):
        v, _ = librosa.load(os.path.join(separate_dir, "vocals.wav"), sr=22050, mono=True)
        m, _ = librosa.load(os.path.join(separate_dir, "no_vocals.wav"), sr=22050, mono=True)
        # pausas de la VOZ (más fiables que sobre la mezcla con música)
        vdb_all = 20 * np.log10(librosa.feature.rms(y=v, frame_length=1024, hop_length=hop)[0] + 1e-9)
        vthr = np.percentile(vdb_all, 95) - 30
        vs, s0 = [], None
        for i, q in enumerate(vdb_all < vthr):
            if q and s0 is None:
                s0 = i
            if not q and s0 is not None:
                if (i - s0) * hop / sr >= 0.2:
                    vs.append([round(i0 * hop / sr, 2) for i0 in (s0, i)])
                s0 = None
        res["silencios_>0.2s"] = vs
        mt, _ = librosa.beat.beat_track(y=m, sr=sr)
        mch = librosa.feature.chroma_cqt(y=m, sr=sr).mean(1)
        res["tempo_bpm_estimado"] = round(float(np.atleast_1d(mt)[0]), 1)
        res["notas_dominantes"] = [names[i] for i in np.argsort(mch)[::-1][:5]]
        res["nota"] = "tempo y notas calculados sobre la pista sin voz"
        vr = librosa.feature.rms(y=v, hop_length=hop)[0]
        mr = librosa.feature.rms(y=m, hop_length=hop)[0]
        vdb, mdb = 20 * np.log10(vr + 1e-9), 20 * np.log10(mr + 1e-9)
        active = vdb > np.percentile(vdb, 95) - 25
        voice_present = active.mean() > 0.15
        harm, perc = librosa.effects.hpss(m)
        hdb = 20 * np.log10(librosa.feature.rms(y=harm, hop_length=hop)[0] + 1e-9)
        pon = librosa.onset.onset_detect(y=perc, sr=22050, units="time", backtrack=False, delta=0.25)
        pstr = librosa.onset.onset_strength(y=perc, sr=22050, hop_length=hop)
        strong = [round(float(x), 2) for x in pon if pstr[min(len(pstr) - 1, int(x * 22050 / hop))] > np.percentile(pstr, 90)]
        aligned = sum(any(abs(c["t"] - s) < 0.2 for s in strong) for c in cuts)
        res["capas"] = {
            "voz_presente": bool(voice_present),
            "voz_rms_db_activa": round(float(np.median(vdb[active])), 1) if active.any() else None,
            "musica_tonal_rms_db": round(float(np.median(hdb)), 1),
            "musica_bajo_voz_db": round(float(np.median(vdb[active]) - np.median(hdb)), 1) if active.any() else None,
            "sfx_candidatos_t": strong,
            "cortes_con_sfx_%": round(100 * aligned / max(1, len(cuts)), 1),
        }
    return res


def separate(wav, outdir, model="htdemucs"):
    sys.path.insert(0, HERE)
    from reference_audio import ensure_demucs_weights

    ensure_demucs_weights(model)
    sh([sys.executable, "-m", "demucs", "-n", model, "--two-stems", "vocals", "-o", outdir, wav])
    base = os.path.splitext(os.path.basename(wav))[0]
    return os.path.join(outdir, model, base)


def transcribe(wav, model, lang):
    import whisper

    m = whisper.load_model(model)
    r = m.transcribe(wav, language=lang, word_timestamps=True)
    words = [{"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)} for seg in r["segments"] for w in seg["words"]]
    return {"texto": r["text"].strip(), "palabras": words}


# ----------------------------------------------------------------------------- hojas de contactos
def contact_sheets(video, outdir, info):
    os.makedirs(os.path.join(outdir, "frames_2fps"), exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", "fps=2", "-q:v", "2", os.path.join(outdir, "frames_2fps", "f_%04d.jpg")])
    fs = sorted(os.listdir(os.path.join(outdir, "frames_2fps")))
    tw = 180
    th = int(tw * info["height"] / info["width"])
    per = 48
    cols = 8
    pages = []
    for p in range(0, len(fs), per):
        chunk = fs[p : p + per]
        rows = math.ceil(len(chunk) / cols)
        S = Image.new("RGB", (cols * tw, rows * (th + 18)), "white")
        d = ImageDraw.Draw(S)
        for k, f in enumerate(chunk):
            im = Image.open(os.path.join(outdir, "frames_2fps", f)).convert("RGB").resize((tw, th))
            x, y = (k % cols) * tw, (k // cols) * (th + 18)
            S.paste(im, (x, y + 18))
            d.text((x + 3, y + 3), f"{(p + k) * 0.5:.1f}s", fill="red")
        name = f"contact_2fps_{p // per + 1:02d}.jpg"
        S.save(os.path.join(outdir, name), quality=85)
        pages.append(name)
    return pages


def shot_sheet(video, outdir, shots, info):
    os.makedirs(os.path.join(outdir, "frames_cortes"), exist_ok=True)
    tw = 200
    th = int(tw * info["height"] / info["width"])
    cols = 8
    rows = math.ceil(len(shots) / cols)
    S = Image.new("RGB", (cols * tw, max(1, rows) * (th + 34)), "white")
    d = ImageDraw.Draw(S)
    for k, s in enumerate(shots):
        t = min(s["start"] + min(0.15, s["dur"] / 3), info["duration"] - 0.05)
        f = os.path.join(outdir, "frames_cortes", f"plano_{k:03d}_{s['start']:.2f}s.jpg")
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-q:v", "2", f])
        if os.path.exists(f):
            im = Image.open(f).convert("RGB").resize((tw, th))
            x, y = (k % cols) * tw, (k // cols) * (th + 34)
            S.paste(im, (x, y + 34))
            d.text((x + 3, y + 3), f"#{k} {s['start']:.2f}s", fill="red")
            d.text((x + 3, y + 17), f"{s['dur']:.2f}s", fill="blue")
    S.save(os.path.join(outdir, "contact_planos.jpg"), quality=85)


# ----------------------------------------------------------------------------- informe
def write_md(a, path):
    L = []
    i = a["video"]
    L.append(f"# Análisis de `{a['archivo']}`\n")
    L.append(f"- {i['width']}×{i['height']} ({i['orientation']}), {i['fps']} fps, {i['duration']:.2f} s, audio: {'sí' if i['has_audio'] else 'no'}")
    r = a["ritmo"]
    L.append("\n## Ritmo de cortes")
    L.append(f"- Planos: {r['planos']} · cortes duros: {r['cortes_duros']} · transiciones suaves: {r['transiciones_suaves']}")
    L.append(f"- Duración de plano: mediana {r['plano_mediana_s']} s · media {r['plano_media_s']} s · min {r['plano_min_s']} s · max {r['plano_max_s']} s")
    L.append(f"- Cortes por minuto: {r['cortes_por_min']} · tiempo con algo cambiando: {r['tiempo_con_cambio_%']} % · eventos visuales/s: {r['eventos_visuales_por_s']}")
    L.append("\n## Planos")
    L.append("| # | inicio | dur | cámara | tema | lum | sat | paleta |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in a["planos"]:
        L.append(f"| {s['i']} | {s['start']:.2f} | {s['dur']:.2f} | {s['camara']['tipo']} ({s['camara']['vel_px_s_1080']} px/s {s['camara']['direccion']}, zoom {s['camara']['zoom_por_s']}/s{', whip' if s['camara']['tiene_whip'] else ''}) | {s['color']['tema']} | {s['color']['luminancia_media']} | {s['color']['saturacion_media']} | {' '.join(p['hex'] for p in s['color']['paleta'][:4])} |")
    if a["transiciones_suaves"]:
        L.append("\nTransiciones suaves (fundido / barrido / whip / zoom): " + ", ".join(f"{x['start']}–{x['end']} s" for x in a["transiciones_suaves"]))
    c = a["color_global"]
    L.append("\n## Color global")
    L.append(f"- Tema {c['tema']}, luminancia {c['luminancia_media']}, saturación {c['saturacion_media']}, monocromo: {c['monocromo']}")
    L.append("- Paleta: " + ", ".join(f"{p['hex']} ({p['peso'] * 100:.0f}%)" for p in c["paleta"]))
    L.append(f"- Grano (Laplaciano en zonas planas): {a['textura']['grano']} · viñeta (esquinas/centro): {a['textura']['vineta']}")
    if a.get("texto"):
        L.append("\n## Texto en pantalla (OCR)")
        for k, v in a["texto"].items():
            L.append(f"- {k}: {v}")
    if a.get("audio"):
        L.append("\n## Audio")
        for k, v in a["audio"].items():
            if k == "capas":
                for k2, v2 in v.items():
                    L.append(f"- capas.{k2}: {v2}")
            elif k != "silencios_>0.2s":
                L.append(f"- {k}: {v}")
        L.append(f"- silencios >0.2 s: {a['audio'].get('silencios_>0.2s')}")
    if a.get("transcripcion"):
        tr = a["transcripcion"]
        L.append("\n## Voz")
        L.append(f"- Texto: «{tr['texto']}»")
        L.append(f"- Palabras/min: {tr.get('ppm')}")
    L.append("\n## Siguiente paso")
    L.append("Mira `contact_planos.jpg` y `contact_2fps_*.jpg`, y amplía fotogramas concretos para identificar tipografías, objetos, transiciones y animaciones. Con estos números rellena `estilo.md`.")
    open(path, "w").write("\n".join(L) + "\n")


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--ocr", action="store_true", help="detectar texto en pantalla con RapidOCR")
    ap.add_argument("--ocr-step", type=float, default=0.25, help="segundos entre fotogramas de OCR")
    ap.add_argument("--separate", action="store_true", help="separar voz/música con Demucs")
    ap.add_argument("--whisper", default=None, help="modelo Whisper para transcribir la referencia (tiny/base/small/medium)")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--sensitivity", type=float, default=1.0, help=">1 detecta más cortes, <1 menos")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    info = probe(args.video)
    print(f"[1/7] {info['width']}x{info['height']} {info['fps']}fps {info['duration']:.2f}s")

    gray = read_frames(args.video, 128)
    fps = len(gray) / info["duration"] if info["duration"] else info["fps"]
    cuts, soft, score, pdiff = detect_cuts(gray, fps, args.sensitivity)
    shots = shots_from_cuts(cuts, info["duration"])
    print(f"[2/7] {len(cuts)} cortes, {len(soft)} transiciones suaves, {len(shots)} planos")

    gmot = read_frames(args.video, 192)
    pans, _ = camera_motion(gmot, len(gmot) / info["duration"], 1080 / 192)
    zs = zoom_samples(read_frames(args.video, 160), len(gmot) / info["duration"])
    rgb = read_frames(args.video, 96, fps=4, gray=False)
    for s in shots:
        a, b = int(s["start"] * fps), max(int(s["start"] * fps) + 1, int(s["end"] * fps) - 1)
        zin = [z for t_, z in zs if s["start"] <= t_ <= s["end"]]
        s["camara"] = classify_motion(pans[a : b - 1] if b - 1 > a else pans[a : a + 1], float(np.median(zin)) if zin else 0.0, pdiff[a : b - 1] if b - 1 > a else pdiff[a : a + 1])
        ra, rb = int(s["start"] * 4), max(int(s["start"] * 4) + 1, int(s["end"] * 4))
        s["color"] = color_stats(rgb[ra:rb] if rb <= len(rgb) else rgb[-1:])
    print("[3/7] cámara y color por plano")

    full = read_frames(args.video, 540, fps=1, gray=False)
    gv = [grain_and_vignette(f) for f in full[: min(len(full), 12)]]
    durs = np.array([s["dur"] for s in shots])
    events = int(((pdiff[1:-1] > pdiff[:-2]) & (pdiff[1:-1] > pdiff[2:]) & (pdiff[1:-1] > 0.006)).sum()) if len(pdiff) > 2 else 0
    analysis = {
        "archivo": os.path.basename(args.video),
        "video": info,
        "ritmo": {
            "planos": len(shots),
            "cortes_duros": len(cuts),
            "transiciones_suaves": len(soft),
            "plano_mediana_s": round(float(np.median(durs)), 2),
            "plano_media_s": round(float(durs.mean()), 2),
            "plano_min_s": round(float(durs.min()), 2),
            "plano_max_s": round(float(durs.max()), 2),
            "cortes_por_min": round(60 * len(cuts) / info["duration"], 1),
            "tiempo_con_cambio_%": round(100 * float((pdiff > 0.004).mean()), 1),
            "eventos_visuales_por_s": round(events / info["duration"], 2),
        },
        "cortes": cuts,
        "transiciones_suaves": soft,
        "planos": shots,
        "color_global": color_stats(rgb),
        "zoom_muestras_(t,zoom_por_s)": zs,
        "textura": {"grano": float(np.median([g for g, _ in gv])), "vineta": float(np.median([v for _, v in gv]))},
    }
    pages = contact_sheets(args.video, args.outdir, info)
    shot_sheet(args.video, args.outdir, shots, info)
    print(f"[4/7] hojas de contactos: {', '.join(pages)} + contact_planos.jpg")

    if args.ocr:
        tl = ocr_timeline(args.video, info, args.ocr_step)
        if tl is not None:
            json.dump(tl, open(os.path.join(args.outdir, "ocr_timeline.json"), "w"), ensure_ascii=False, indent=1)
            analysis["texto"] = summarize_text(tl)
    print("[5/7] texto en pantalla" + (" (OCR)" if args.ocr else " (omitido, usa --ocr)"))

    sep_dir = None
    if info["has_audio"]:
        wav = os.path.join(args.outdir, "audio.wav")
        sh(["ffmpeg", "-v", "error", "-y", "-i", args.video, "-vn", "-ac", "2", "-ar", "44100", wav])
        if args.separate:
            try:
                sep_dir = separate(wav, os.path.join(args.outdir, "separado"))
            except Exception as e:  # noqa: BLE001
                print(f"  [demucs] no se pudo separar: {e}", file=sys.stderr)
        analysis["audio"] = audio_analysis(wav, cuts, sep_dir)
        if sep_dir:
            analysis["audio"]["separado_en"] = sep_dir
        print("[6/7] audio")
        if args.whisper:
            tr = transcribe(wav, args.whisper, args.lang)
            nwords = len(tr["palabras"])
            span = (tr["palabras"][-1]["e"] - tr["palabras"][0]["s"]) if nwords > 1 else 0
            tr["ppm"] = round(60 * nwords / span, 1) if span else None
            json.dump(tr, open(os.path.join(args.outdir, "transcripcion.json"), "w"), ensure_ascii=False, indent=1)
            analysis["transcripcion"] = {"texto": tr["texto"], "ppm": tr["ppm"], "palabras": nwords}
    print("[7/7] informe")
    json.dump(analysis, open(os.path.join(args.outdir, "analysis.json"), "w"), ensure_ascii=False, indent=1)
    write_md(analysis, os.path.join(args.outdir, "analisis.md"))
    print(f"Listo: {os.path.join(args.outdir, 'analisis.md')}")


if __name__ == "__main__":
    main()
