#!/usr/bin/env python3
"""Limpia y nivela la voz de cada toma (misma duración y tiempos que el clip de origen).
Cadena: paso-alto 90 Hz (viento) → reducción de ruido suave → realce de presencia →
compresión → nivelado a -15 LUFS medido solo sobre el tramo hablado → limitador a -1,5 dBTP."""
import subprocess, json, re, sys
TRAMOS = {  # clip: (inicio, fin) del discurso en segundos de origen
    "toma1_agro": (1.75, 5.95), "wa_105147_0": (1.48, 10.70), "wa_105147_1": (2.30, 8.00),
    "wa_105147_2": (2.18, 5.08), "wa_105147_3": (2.28, 7.02), "wa_105147_4": (1.50, 5.66), "wa_105147_5": (1.93, 4.33),
}
CADENA = "highpass=f=90,afftdn=nr=9:nf=-45:tn=1,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=240:t=q:w=1.0:g=-2,acompressor=threshold=-20dB:ratio=3:attack=8:release=140:makeup=2"
OBJ = -15.0
for clip, (a, b) in TRAMOS.items():
    src = f"material/crudo/{clip}.mp4"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-to", str(b), "-i", src, "-vn",
                        "-af", CADENA + ",ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    lufs = float(m[-1]); gan = OBJ - lufs
    out = f"public/voz/{clip}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-af",
                    f"{CADENA},volume={gan:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled",
                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out], check=True)
    chk = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-to", str(b), "-i", out, "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    print(f"{clip}: medido {lufs:.1f} LUFS → ganancia {gan:+.1f} dB → resultado {re.findall(r'I:\s+(-?[\d.]+) LUFS', chk)[-1]} LUFS, pico {re.findall(r'Peak:\s+(-?[\d.]+) dBFS', chk)[-1]} dBFS")
