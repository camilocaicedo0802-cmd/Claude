"""Reprocesa SOLO el audio de cada toma con ganancia medida (EBU R128) y lo vuelve a unir al vídeo ya exportado."""
import json, subprocess, os, re
E=json.load(open("material/edl.json")); OUT="public/media/aroll"
def chain(src):
    if "testimonio" in src:
        return "highpass=f=100,afftdn=nr=22:nf=-34,equalizer=f=3800:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=140:makeup=3"
    return "highpass=f=85,afftdn=nr=10:nf=-48,equalizer=f=240:t=q:w=1:g=-2,equalizer=f=4500:t=q:w=1.2:g=3,acompressor=threshold=-26dB:ratio=3.5:attack=6:release=120:makeup=8"
def agraph(o, extra):
    parts=[]; aa=""
    for i,(a,b) in enumerate(o["keep"]):
        d=b-a; fo=0.035 if ("testimonio" in o["src"] and i==len(o["keep"])-1) else 0.02
        parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0,d-fo):.3f}:d={fo}[a{i}]"); aa+=f"[a{i}]"
    parts.append(f"{aa}concat=n={len(o['keep'])}:v=0:a=1,{chain(o['src'])}{extra}[ao]")
    return ";".join(parts)
for o in E:
    src="material/"+o["src"]; vid=f"{OUT}/{o['id']}.mp4"; tmp=f"{OUT}/{o['id']}.tmp.mp4"; wav=f"{OUT}/{o['id']}.wav"
    r=subprocess.run(["ffmpeg","-hide_banner","-i",src,"-filter_complex",agraph(o,",ebur128=peak=true"),"-map","[ao]","-f","null","-"],capture_output=True,text=True).stderr
    m=re.findall(r"I:\s+(-?[0-9.]+) LUFS",r); li=float(m[-1]); gain=-15.0-li
    subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",agraph(o,f",volume={gain:.2f}dB,alimiter=limit=0.89:attack=3:release=60:level=disabled,aresample=48000,apad=pad_dur=0.40"),"-map","[ao]","-c:a","pcm_s16le",wav],check=True)
    subprocess.run(["ffmpeg","-v","error","-y","-i",vid,"-i",wav,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",tmp],check=True)
    os.replace(tmp,vid); os.remove(wav)
    r2=subprocess.run(["ffmpeg","-hide_banner","-i",vid,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
    print(f"{o['id']}: {li:.1f} LUFS → gain {gain:+.1f} dB → {re.findall(r'I:\s+(-?[0-9.]+) LUFS',r2)[-1]} LUFS, pico {re.findall(r'Peak:\s+(-?[0-9.]+) dBFS',r2)[-1]} dBFS",flush=True)
