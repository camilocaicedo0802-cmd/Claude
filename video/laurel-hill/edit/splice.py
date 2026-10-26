"""Re-render a time window and build the final YouTube file in one encode.

usage: python splice.py MASTER.mp4 MIX.wav OUT.mp4 [T_START T_END ...]
Each (T_START, T_END) window is re-rendered from the timeline and replaces that part of MASTER."""
import os
import subprocess
import sys

master, mix, out = sys.argv[1], sys.argv[2], sys.argv[3]
wins = [(float(a), float(b)) for a, b in zip(sys.argv[4::2], sys.argv[5::2])]
here = os.path.dirname(os.path.abspath(__file__))
work = os.path.join(os.path.dirname(os.path.abspath(out)), "splice")
os.makedirs(work, exist_ok=True)
FPS = 30
inputs = ["-i", master]
parts = []  # (input_idx, start, end) in seconds
cur = 0.0
for k, (a, b) in enumerate(wins):
    fa, fb = int(a * FPS), int(round(b * FPS))
    a, b = fa / FPS, fb / FPS
    seg = os.path.join(work, f"seg{k}.mp4")
    if not os.path.exists(seg):
        subprocess.run([sys.executable, "-I", os.path.join(here, "render.py"), seg, "--workers", "1",
                        "--from", f"{a:.6f}", "--to", f"{b:.6f}"], check=True)
    inputs += ["-i", seg]
    parts.append((0, cur, a))
    parts.append((k + 1, 0.0, b - a))
    cur = b
parts.append((0, cur, None))
fc = []
for j, (idx, s, e) in enumerate(parts):
    trim = f"trim=start={s:.6f}" + (f":end={e:.6f}" if e is not None else "")
    fc.append(f"[{idx}:v]{trim},setpts=PTS-STARTPTS[v{j}]")
fc.append("".join(f"[v{j}]" for j in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[vout]")
ai = len(wins) + 1
fc.append(f"[{ai}:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
cmd = ["ffmpeg", "-v", "error", "-stats", "-y"] + inputs + ["-i", mix, "-filter_complex", ";".join(fc),
       "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "grain",
       "-maxrate", "10M", "-bufsize", "20M", "-pix_fmt", "yuv420p", "-r", "30", "-g", "60",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out]
subprocess.run(cmd, check=True)
print("wrote", out)
