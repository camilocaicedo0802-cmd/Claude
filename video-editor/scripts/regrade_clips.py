"""Vuelve a gradar las tomas con el GRADE actual de prepare_clips.py SIN repetir los recortes:
1) recodifica public/clips/<clip>.mp4 desde el bruto (mismos fotogramas, voz original);
2) rehace <clip>_fg.webm con el RGB nuevo y la transparencia (alfa) del webm existente.
Uso: python3 -I regrade_clips.py [clips...]"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, "/home/user/Claude/video-editor/scripts")
import prepare_clips as P  # noqa: E402

OW, OH = 1080, 1920
only = set(sys.argv[1:])
for clip, a, b, _ in P.SEGMENTS:
    if clip == "s7_vo" or (only and clip not in only):
        continue
    dur = b - a
    mp4 = f"{P.OUT}/{clip}.mp4"
    wav = f"{P.OUT}/{clip}.wav"
    tmp = f"{P.TMP}/{clip}_regrade.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", P.SRC, "-i", wav, "-t", f"{dur:.3f}",
                    "-map", "0:v:0", "-map", "1:a:0", "-vf", f"scale=1440:2560:flags=lanczos,fps=30,{P.GRADE}",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", tmp], check=True)
    fg_old = f"{P.OUT}/{clip}_fg.webm"
    fg_tmp = f"{P.TMP}/{clip}_fg_regrade.webm"
    rgb = subprocess.Popen(["ffmpeg", "-v", "error", "-i", tmp, "-vf", f"scale={OW}:{OH}:flags=lanczos",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    alp = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", fg_old,
                            "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{OW}x{OH}",
                            "-r", "30", "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0",
                            "-crf", "12", "-deadline", "good", "-cpu-used", "2", "-row-mt", "1",
                            "-auto-alt-ref", "0", fg_tmp], stdin=subprocess.PIPE)
    n = 0
    while True:
        c = rgb.stdout.read(OW * OH * 3)
        d = alp.stdout.read(OW * OH * 4)
        if len(c) < OW * OH * 3 or len(d) < OW * OH * 4:
            break
        frame = np.frombuffer(c, np.uint8).reshape(OH, OW, 3)
        alpha = np.frombuffer(d, np.uint8).reshape(OH, OW, 4)[..., 3]
        enc.stdin.write(np.dstack([frame, alpha]).tobytes())
        n += 1
    enc.stdin.close(); enc.wait(); rgb.wait(); alp.wait()
    os.replace(tmp, mp4)
    os.replace(fg_tmp, fg_old)
    print(f"ok {clip}: {n} fotogramas", flush=True)
