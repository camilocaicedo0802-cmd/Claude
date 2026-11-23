"""Copia a public/media/sfx SOLO efectos de las carpetas del cliente (material/drive/SFX), recortados y normalizados."""
import librosa, numpy as np, soundfile as sf, json, os, warnings
warnings.filterwarnings("ignore")
B="material/drive/SFX/"; OUT="public/media/sfx/"
M={ # nombre: (archivo original, [inicio, fin] opcional en s)
 "swish_a":("SFX PACK 1/Swoosh 01 - 03.wav",None), "swish_b":("SFX PACK 2/Swoosh 01 - 06.wav",None),
 "whoosh_1":("SFX PACK 1/VS_Short Whoosh 1.mp3",None), "whoosh_2":("SFX PACK 1/VS_Short Whoosh 3.mp3",None), "whoosh_3":("SFX PACK 2/VS_Short Whoosh 6.mp3",None),
 "whoosh_deep":("SFX PACK 1/Woosh Effect 3.wav",None), "whoosh_fast":("SFX PACK 1/Woosh Effect 5.wav",None),
 "riser":("SFX PACK 1/RISER.mp3",None), "pop":("SFX PACK 1/Pop up SFX.mp3",None),
 "key_1":("SFX PACK 2/Teclas-Clicks/Mechanical Keyboard Click 05.wav",None), "key_2":("SFX PACK 2/Teclas-Clicks/Mechanical Keyboard Click 13.wav",None),
 "key_3":("SFX PACK 2/Teclas-Clicks/Mechanical Keyboard Click 17.wav",None), "key_4":("SFX PACK 2/Teclas-Clicks/Mechanical Keyboard Click 19.wav",None),
 "key_5":("SFX PACK 1/Tecla.mp3",None), "keys_multi":("SFX PACK 2/Teclas-Clicks/Mechanical Keyboard Multiple Clicks 01.wav",None),
 "click_1":("SFX PACK 2/Teclas-Clicks/Mouse Click 04.wav",None), "click_2":("SFX PACK 2/Teclas-Clicks/Mouse Click 02.wav",None),
 "click_double":("SFX PACK 2/Teclas-Clicks/Lighter Double Click 02.wav",None),
 "shutter":("SFX PACK 2/SFX General/Camera Flash.mp3",None), "shutter_click":("SFX PACK 2/Teclas-Clicks/Camera Shutter Click 01.wav",None),
 "notif":("SFX PACK 2/SFX General/snapchat-notification-sound.mp3",None),
 "sub_hit":("SFX PACK 1/Sub Bass Hit.wav",None), "sub_drop":("SFX PACK 1/Sub Bass Drop 2.wav",None), "boom":("SFX PACK 1/Boom 2.mp3",None), "bass_hit":("SFX PACK 1/Deep Bass Hit 1.wav",None),
 "marker":("SFX PACK 1/Subrayado rotulador.mp3",None), "tick":("SFX PACK 1/RELOJ.mp3",None), "error":("SFX PACK 1/Acierto y error.mp3",None),
 "disappear":("SFX PACK 1/disappear.wav",None), "snap":("SFX PACK 1/Chasquido épico.mpeg",None),
}
meta={}
for k,(f,rng) in M.items():
    p=B+f
    y,sr=librosa.load(p,sr=48000,mono=True)
    env=np.abs(y); pk=env.max(); i0=max(0,int(np.argmax(env>pk*0.04))-int(0.008*sr)); i1=min(len(y),len(env)-int(np.argmax(env[::-1]>pk*0.02))+int(0.05*sr))
    y=y[i0:i1]; y=y/np.abs(y).max()*0.708
    n=int(0.03*sr); y[-n:]*=np.linspace(1,0,n); y[:48]*=np.linspace(0,1,48)
    sf.write(OUT+k+".wav",y,sr,subtype="PCM_16")
    e=np.abs(y); peak_at=float(np.argmax(e)/sr)
    rms=librosa.feature.rms(y=y,frame_length=2048,hop_length=480)[0]
    meta[k]=dict(original=f,duracion=round(len(y)/sr,3),picoEn=round(peak_at,3))
    print(f"{k:14s} {len(y)/sr:5.2f}s pico@{peak_at:5.2f}  ← {f}")
json.dump(meta,open("src/data/sfx.json","w"),ensure_ascii=False,indent=1)
