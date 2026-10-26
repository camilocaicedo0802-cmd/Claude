"""Re-render time windows and build the final YouTube file.

usage: python splice.py MASTER.mp4 MIX.wav OUT.mp4 [T_START T_END ...]
Each (T_START, T_END) window is re-rendered from the timeline and replaces that part of MASTER.
The video is encoded in 90 s pieces (constant memory, resumable) and joined without re-encoding;
the audio gets a two-pass loudnorm to -14 LUFS."""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

FPS = 30
PIECE = 90 * FPS
X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "grain", "-maxrate", "10M",
        "-bufsize", "20M", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "60", "-an"]
LOUD = "loudnorm=I=-14:TP=-1.5:LRA=11"


def nframes(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_frames", "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def encode_piece(job):
    src, first, n, dst = job
    if os.path.exists(dst):
        return dst
    seek = ["-ss", f"{(first - 0.5) / FPS:.6f}"] if first else []
    tmp = dst + ".part.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + seek + ["-i", src, "-frames:v", str(n)] + X264 + [tmp],
                   check=True)
    got = nframes(tmp)
    if got != n:
        raise RuntimeError(f"{dst}: {got} frames, expected {n}")
    os.replace(tmp, dst)
    print(f"piece {os.path.basename(dst)} ok ({n} frames)", flush=True)
    return dst


def main():
    master, mix, out = sys.argv[1], sys.argv[2], sys.argv[3]
    wins = [(float(a), float(b)) for a, b in zip(sys.argv[4::2], sys.argv[5::2])]
    here = os.path.dirname(os.path.abspath(__file__))
    work = os.path.join(os.path.dirname(os.path.abspath(out)), "splice")
    os.makedirs(work, exist_ok=True)

    spans = []  # (source, first frame, frame count)
    cur = 0
    for k, (a, b) in enumerate(wins):
        fa, fb = int(a * FPS), int(round(b * FPS))
        seg = os.path.join(work, f"seg{k}.mp4")
        if not os.path.exists(seg):
            subprocess.run([sys.executable, "-I", os.path.join(here, "render.py"), seg, "--workers", "1",
                            "--from", f"{fa / FPS:.6f}", "--to", f"{fb / FPS:.6f}"], check=True)
        spans += [(master, cur, fa - cur), (seg, 0, fb - fa)]
        cur = fb
    spans.append((master, cur, nframes(master) - cur))

    jobs = []
    for src, first, n in spans:
        for s in range(0, n, PIECE):
            jobs.append((src, first + s, min(PIECE, n - s), os.path.join(work, f"piece_{len(jobs):03d}.mp4")))
    with ThreadPoolExecutor(2) as ex:
        pieces = list(ex.map(encode_piece, jobs))
    lst = os.path.join(work, "pieces.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in pieces)

    probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix, "-af", LOUD + ":print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True, check=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    af = (f"{LOUD}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    aac = os.path.join(work, "audio.m4a")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mix, "-af", af, "-c:a", "aac", "-b:a", "192k", aac], check=True)

    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", aac,
                    "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", out], check=True)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
