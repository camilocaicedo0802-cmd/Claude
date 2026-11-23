import whisper, json, sys, os, subprocess, re, numpy as np
m = whisper.load_model("turbo", download_root="whisper-models")
SR=16000
for name in sys.argv[1:]:
    wav=f"audio16k/{name}.wav"
    out=subprocess.run(["ffmpeg","-v","info","-i",wav,"-af","silencedetect=noise=-36dB:d=0.18","-f","null","-"],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",out)]; en=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",out)]
    audio=whisper.load_audio(wav); dur=len(audio)/SR
    # speech = complement of silences
    cuts=[0.0]; 
    for s,e in zip(st,en+[dur]*(len(st)-len(en))): cuts+= [s,e]
    cuts.append(dur); sp=[(cuts[i],cuts[i+1]) for i in range(0,len(cuts)-1,2) if cuts[i+1]-cuts[i]>0.3]
    segs=[]
    for a,b in sp:
        a2,b2=max(0,a-0.12),min(dur,b+0.15)
        r=m.transcribe(audio[int(a2*SR):int(b2*SR)], language="es", word_timestamps=True, fp16=False, condition_on_previous_text=False, temperature=0)
        for s in r["segments"]:
            ws=[dict(word=w["word"],start=round(w["start"]+a2,3),end=round(w["end"]+a2,3),probability=w.get("probability")) for w in s.get("words",[])]
            if ws: segs.append(dict(start=ws[0]["start"],end=ws[-1]["end"],text=s["text"],words=ws,avg_logprob=s["avg_logprob"],no_speech_prob=s["no_speech_prob"]))
    json.dump(dict(text=" ".join(s["text"].strip() for s in segs),segments=segs,language="es",metodo="trozos"), open(f"transcripciones/{name}.json","w"), ensure_ascii=False, indent=1)
    print("==",name); [print(f"  {s['start']:6.2f}-{s['end']:6.2f} {s['text'].strip()}") for s in segs]
