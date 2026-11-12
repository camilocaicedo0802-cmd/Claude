"""Asset definitions + mezzanine prep.

crop = [cx, cy, zoom]: centre of the crop window in normalised source coords, and zoom relative to the
largest window of the target aspect that fits in the source (1 = cover-fit).
out  = "full" (mezz 1188x2112, 9:16) or "half" (mezz 1188x1056, 9:8). Mezzanines carry 10% headroom for
slow push-ins in the compositor.
top  = for problem assets: which row (0..1 of the full frame) is centred in the top half after the split.
"""
import json, os, subprocess, sys

W = sys.argv[1] if len(sys.argv) > 1 else "."
B = os.path.join(W, "brollA")
B2 = os.path.join(W, "broll2")
ST = os.path.join(W, "stock", "full")
RAW = os.path.join(W, "raw")
idx = dict(l.rstrip("\n").split("\t") for l in open(os.path.join(W, "photos_idx.txt")))
PH = lambda n: os.path.join(B, idx[str(n)])

ASSETS = {
    # hook (full screen b-roll, only the first 2.6 s)
    "hook": dict(type="video", src=f"{B}/Spray_tan_3_Videos_Proceso_MVI_4551.MP4", t_in=0.25, dur=3.2, crop=[0.5, 0.42, 1.12], out="full", kb=[1.0, 1.07]),
    # problem cards (top) / solution cards (bottom): wide 2.23:1 support visuals
    "p1_pale": dict(type="video", src=f"{B}/Spray_Tan_1_spray_tan_1_-_B_roll_antes_IMG_4082.MOV", t_in=2.3, dur=4.2, crop=[0.5, 0.36, 1.0], out="card", kb=[1.0, 1.06]),
    "s1_after": dict(type="video", src=f"{B}/Spray_Tan_1_spray_tan_1_-_B_roll_despues_IMG_4149.MOV", t_in=0.0, dur=2.8, crop=[0.5, 0.27, 1.0], out="card", kb=[1.0, 1.06]),
    "p2_asap": dict(type="photo", src=f"{ST}/H_asap_1.jpg", crop=[0.5, 0.53, 1.05], out="card", kb=[1.0, 1.10]),
    "s2_spray": dict(type="video", src=f"{B}/Spray_Tan_1_spray_tan_1_-_B_roll_proceso_IMG_4102.MOV", t_in=0.10, dur=3.8, crop=[0.45, 0.45, 1.0], out="card", kb=[1.0, 1.06]),
    "p3_dry": dict(type="photo", src=f"{ST}/B_dryskin_2.jpg", crop=[0.5, 0.5, 1.0], out="card", kb=[1.0, 1.10]),
    "s3_exfoliate": dict(type="photo", src=f"{ST}/A_exfoliate_1.jpg", crop=[0.5, 0.50, 1.0], out="card", kb=[1.0, 1.10]),
    "s3_exfoliate2": dict(type="photo", src=f"{W}/stock/A_exfoliate/6_Z75dEgdKCS0.jpg", crop=[0.5, 0.5, 1.0], out="card", kb=[1.0, 1.10]),
    "p4_fading": dict(type="photo", src=f"{ST}/D_fading_2.jpg", crop=[0.5, 0.60, 1.0], out="card", kb=[1.0, 1.10]),
    "s4_moisturize": dict(type="photo", src=f"{ST}/C_moisturize_2.jpg", crop=[0.48, 0.5, 1.0], out="card", kb=[1.0, 1.10]),
    "p5_hands": dict(type="video", src=f"{B}/Spray_Tan_1_spray_tan_1_-_B_roll_proceso_IMG_4099.MOV", t_in=1.4, dur=7.2, crop=[0.5, 0.64, 1.0], out="card", kb=[1.0, 1.05]),
    "s5_barrier": dict(type="video", src=f"{B}/Spray_tan_2_Videos_Consulta_antes_de_bronceado_IMG_1949.MOV", t_in=19.0, dur=5.0, crop=[0.25, 0.48, 1.8], out="card", kb=[1.0, 1.04]),
    "p6_vacation": dict(type="photo", src=f"{ST}/F_vacation_1.jpg", crop=[0.5, 0.45, 1.0], out="card", kb=[1.0, 1.10]),
    "s6_glow": dict(type="video", src=f"{B}/Spray_tan_3_Videos_Despu_s_IMG_2211.MOV", t_in=0.0, dur=4.4, crop=[0.45, 0.265, 1.15], out="card", kb=[1.0, 1.05]),
    "p7_event": dict(type="photo", src=f"{ST}/G_event_1.jpg", crop=[0.55, 0.30, 1.0], out="card", kb=[1.0, 1.10]),
    "s7_event": dict(type="photo", src=PH(99), crop=[0.5, 0.42, 1.0], out="card", kb=[1.0, 1.08]),
    "s7_spray": dict(type="video", src=f"{B}/Spray_tan_3_Videos_Proceso_MVI_4545.MP4", t_in=6.2, dur=4.0, crop=[0.5, 0.30, 1.0], out="card", kb=[1.0, 1.04]),
    "p8_unsure": dict(type="video", src=f"{B}/Spray_tan_2_Videos_Llegada_al_sal_n_IMG_1944.MOV", t_in=0.8, dur=7.2, crop=[0.45, 0.66, 1.25], out="card", kb=[1.0, 1.05]),
    "s8_consult": dict(type="video", src=f"{B}/Spray_tan_2_Videos_Consulta_antes_de_bronceado_IMG_1948.MOV", t_in=0.3, dur=4.6, crop=[0.42, 0.355, 1.0], out="card", kb=[1.0, 1.04]),
    # outro support: polaroids of results + Slate cards
    "o_res1": dict(type="photo", src=PH(70), crop=[0.5, 0.34, 1.35], out="pol", kb=[1.0, 1.06]),
    "o_res2": dict(type="photo", src=PH(92), crop=[0.5, 0.38, 1.25], out="pol", kb=[1.0, 1.06]),
    "o_res3": dict(type="photo", src=PH(200), crop=[0.5, 0.36, 1.2], out="pol", kb=[1.0, 1.06]),
    "o_slate": dict(type="video", src=f"{B2}/IMG_0822.MOV", t_in=0.4, dur=2.6, crop=[0.5, 0.29, 1.0], out="card", kb=[1.0, 1.05]),
    "o_desk": dict(type="video", src=f"{B2}/IMG_0816.MOV", t_in=0.0, dur=1.85, crop=[0.5, 0.55, 1.0], out="card", kb=[1.0, 1.05]),
}

SIZE = {"full": (1188, 2112), "half": (1188, 1056), "card": (1092, 490), "pol": (317, 363)}


def probe(path):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:stream_side_data=rotation", "-of", "json", path],
                                  capture_output=True, text=True).stdout)["streams"][0]
    w, h = d["width"], d["height"]
    rot = 0
    for sd in d.get("side_data_list", []):
        rot = int(sd.get("rotation", 0))
    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h


def window(sw, sh, aspect, cx, cy, zoom):
    # largest window of `aspect` (w/h) inside the source, scaled by 1/zoom, centred at (cx, cy)
    if sw / sh > aspect:
        wh = sh; ww = sh * aspect
    else:
        ww = sw; wh = sw / aspect
    ww /= zoom; wh /= zoom
    x = min(max(cx * sw - ww / 2, 0), sw - ww)
    y = min(max(cy * sh - wh / 2, 0), sh - wh)
    return int(round(x)), int(round(y)), int(round(ww)) // 2 * 2, int(round(wh)) // 2 * 2


def prep(aid, a, outdir, force=False):
    tw, th = SIZE[a["out"]]
    if a["type"] == "video":
        dst = os.path.join(outdir, aid + ".mp4")
        if os.path.exists(dst) and not force:
            return dst
        sw, sh = probe(a["src"])
        x, y, ww, wh = window(sw, sh, tw / th, *a["crop"])
        vf = f"crop={ww}:{wh}:{x}:{y},scale={tw}:{th}:flags=lanczos,fps=30,setsar=1,format=yuv420p"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a["t_in"]), "-t", str(a["dur"]), "-i", a["src"],
                        "-an", "-vf", vf, "-c:v", "libx264", "-crf", "9", "-preset", "fast", dst], check=True)
        return dst
    from PIL import Image, ImageOps
    import pillow_heif
    pillow_heif.register_heif_opener()
    dst = os.path.join(outdir, aid + ".png")
    if os.path.exists(dst) and not force:
        return dst
    im = ImageOps.exif_transpose(Image.open(a["src"])).convert("RGB")
    x, y, ww, wh = window(im.width, im.height, tw / th, *a["crop"])
    im = im.crop((x, y, x + ww, y + wh)).resize((tw, th), Image.LANCZOS)
    im.save(dst)
    return dst


if __name__ == "__main__":
    outdir = os.path.join(W, "mezz")
    os.makedirs(outdir, exist_ok=True)
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    from concurrent.futures import ThreadPoolExecutor
    def job(item):
        aid, a = item
        p = prep(aid, a, outdir, force=bool(only))
        return aid, p
    items = [(k, v) for k, v in ASSETS.items() if not only or k in only]
    with ThreadPoolExecutor(3) as ex:
        for aid, p in ex.map(job, items):
            print("ok", aid, p)
    meta = {k: {kk: vv for kk, vv in v.items() if kk != "src"} | {"file": os.path.join(outdir, k + (".mp4" if v["type"] == "video" else ".png"))} for k, v in ASSETS.items()}
    json.dump(meta, open(os.path.join(W, "assets.json"), "w"), indent=1)
