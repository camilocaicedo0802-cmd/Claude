"""Decode the main take (31.0-48.3s) once and run Robust Video Matting continuously over it,
so the alpha is temporally stable. Saves frames, alpha and decontaminated foreground as memmaps."""
import subprocess, sys, os, numpy as np, onnxruntime as ort, time
os.chdir(sys.argv[1])
T0, T1, FPS, Wd, Hd = 31.0, 48.3, 30, 720, 1280
N = int(round((T1 - T0) * FPS))
os.makedirs("work/rvm", exist_ok=True)
frames = np.lib.format.open_memmap("work/rvm/frames.npy", "w+", np.uint8, (N, Hd, Wd, 3))
pha = np.lib.format.open_memmap("work/rvm/pha.npy", "w+", np.uint8, (N, Hd, Wd))
fgr = np.lib.format.open_memmap("work/rvm/fgr.npy", "w+", np.uint8, (N, Hd, Wd, 3))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(T0), "-i", "raw/toma_ugc.mov", "-an", "-vf", f"fps={FPS}",
                      "-frames:v", str(N), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
for i in range(N):
    b = p.stdout.read(Wd * Hd * 3)
    frames[i] = np.frombuffer(b, np.uint8).reshape(Hd, Wd, 3) if len(b) == Wd * Hd * 3 else frames[i - 1]
p.wait()
o = ort.SessionOptions(); o.intra_op_num_threads = 4
s = ort.InferenceSession("models/rvm_720x1280.onnx", o)
rec = {i.name: np.zeros(i.shape, np.float32) for i in s.get_inputs() if i.name.startswith("r")}
t = time.time()
for i in range(N):
    x = (frames[i].astype(np.float32) / 255).transpose(2, 0, 1)[None]
    out = s.run(None, {"src": x, **rec})
    names = [o_.name for o_ in s.get_outputs()]
    res = dict(zip(names, out))
    for k in list(rec):
        rec[k] = res[k.replace("i", "o")]
    pha[i] = (np.clip(res["pha"][0, 0], 0, 1) * 255 + 0.5).astype(np.uint8)
    fgr[i] = (np.clip(res["fgr"][0].transpose(1, 2, 0), 0, 1) * 255 + 0.5).astype(np.uint8)
    if i % 100 == 0:
        print(i, N, round(time.time() - t, 1), flush=True)
frames.flush(); pha.flush(); fgr.flush()
print("done", N, T0, FPS)
