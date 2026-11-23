"""Exporta cada segmento del montaje (public/media/aroll/*.mp4) con silencios quitados y voz procesada."""
import json, subprocess, os, re, sys
E=json.load(open("material/edl.json")); OUT="public/media/aroll"; os.makedirs(OUT,exist_ok=True)
FULL4K={"s01_hook","s13_repitas","s14_comenta"}
TAIL=0.40
def chain(src):
    if "testimonio" in src:
        return "highpass=f=100,afftdn=nr=22:nf=-34,equalizer=f=3800:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=140:makeup=3"
    return "highpass=f=85,afftdn=nr=10:nf=-48,equalizer=f=240:t=q:w=1:g=-2,equalizer=f=4500:t=q:w=1.2:g=3,acompressor=threshold=-26dB:ratio=3.5:attack=6:release=120:makeup=8"
def graph(o, extra_a):
    n=len(o["keep"]); parts=[]; va=""
    for i,(a,b) in enumerate(o["keep"]):
        d=b-a
        vb=b+TAIL if i==n-1 else b
        parts.append(f"[0:v]trim={a}:{vb},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0,d-0.02):.3f}:d=0.02[a{i}]")
        va+=f"[v{i}][a{i}]"
    scale="" if (o["id"] in FULL4K or "testimonio" in o["src"]) else ",scale=2560:1440:flags=lanczos"
    vs="".join(f"[v{i}]" for i in range(n)); as_="".join(f"[a{i}]" for i in range(n))
    parts.append(f"{vs}concat=n={n}:v=1:a=0,fps=24{scale},format=yuv420p[vo];{as_}concat=n={n}:v=0:a=1,{chain(o['src'])}{extra_a},apad=pad_dur={TAIL}[ao]")
    return ";".join(parts)
for o in E:
    dst=f"{OUT}/{o['id']}.mp4"
    if os.path.exists(dst) and "--force" not in sys.argv: continue
    src="material/"+o["src"]
    # 1) medir sonoridad tras la cadena
    li=-24.0; gain=0.0  # la ganancia definitiva la aplica material/audio_tomas.py
    subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",graph(o,f",volume={gain:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled,aresample=48000"),
        "-map","[vo]","-map","[ao]","-c:v","libx264","-crf","17","-preset","veryfast","-g","24","-bf","2","-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",dst],check=True)
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",dst],capture_output=True,text=True).stdout)
    print(f"{o['id']}: in {li:.1f} LUFS, gain {gain:+.1f} dB, dur {d:.2f}s (esperado {o['duration']:.2f}) {os.path.getsize(dst)/1e6:.1f} MB",flush=True)
print("EXPORT_DONE")
