"""Recorta a la persona con Robust Video Matting (ONNX) y genera un WebM VP9 con alfa
(solo la persona, el fondo transparente), para poner texto DETRÁS del sujeto en Remotion.
Uso: python3 scripts/recortar_persona.py <entrada.mp4> <salida.webm> [downsample=0.25] [max_frames]
"""
import subprocess, sys, json, time
import numpy as np, onnxruntime as ort

src, dst = sys.argv[1], sys.argv[2]
ds = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
maxf = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                  "stream=width,height,r_frame_rate", "-of", "json", src], capture_output=True, text=True).stdout)["streams"][0]
W, H = info["width"], info["height"]; fps = info["r_frame_rate"]
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession("modelos/rvm_mobilenetv3_fp32.onnx", so, providers=["CPUExecutionProvider"])
rec = [np.zeros([1, 1, 1, 1], dtype=np.float32)] * 4
dsr = np.array([ds], dtype=np.float32)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", fps, "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M", "-deadline", "realtime", "-cpu-used", "8",
                        "-row-mt", "1", "-auto-alt-ref", "0", dst], stdin=subprocess.PIPE)
n = 0; t0 = time.time()
while n < maxf:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    x = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
    fgr, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dsr})
    a = np.clip(pha[0, 0], 0, 1)
    rgba = np.dstack([img, (a * 255).astype(np.uint8)])
    enc.stdin.write(rgba.tobytes()); n += 1
    if n % 100 == 0: print(f"{n} fotogramas · {n/(time.time()-t0):.1f} fps", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
print(f"OK {n} fotogramas en {time.time()-t0:.0f}s -> {dst}")
