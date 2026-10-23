#!/usr/bin/env python3
"""Build the VSL soundtrack: pitch voice + testimonial voice, epic music ducked underneath.

Usage:
    python3 audio.py --work <dir> --music <track> --music-start 15.85 --out mix.wav

<work> holds voice_raw.wav (edited pitch) and testi_voice.wav (condensed testimonial).
Durations come from render.py, so picture and sound always line up.
"""
import argparse
import os
import subprocess

from render import MAIN_LEN, TOTAL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--music-start", type=float, default=15.85)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    voice = os.path.join(args.work, "voice_raw.wav")
    testi = os.path.join(args.work, "testi_voice.wav")
    graph = (
        # pitch voice (outdoors, phone mic): rumble cut, gentle denoise, presence, leveling
        "[0:a]highpass=f=85,afftdn=nr=10:nf=-32,equalizer=f=3200:t=q:w=1.2:g=2.5,"
        "equalizer=f=250:t=q:w=1:g=-2,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=3,"
        f"loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,apad,atrim=0:{MAIN_LEN:.4f}[v1];"
        # testimonial (lapel mic): rumble cut and the same leveling, matched in loudness
        "[1:a]highpass=f=80,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=90:makeup=2,"
        "loudnorm=I=-16:TP=-2:LRA=7,aresample=48000[v2];"
        f"[v1][v2]concat=n=2:v=0:a=1,apad=whole_dur={TOTAL:.4f},asplit=2[v][key];"
        # music: its break falls under "a otro nivel" and the drop opens the testimonial
        f"[2:a]atrim=start={args.music_start}:duration={TOTAL:.4f},asetpts=PTS-STARTPTS,"
        # the track's soft build-up (until its first hit, 6 s in) is lifted so the bed is there from frame one
        "aresample=48000,volume=0.30,volume='if(lt(t,6.0),2.4,1)':eval=frame,"
        f"afade=t=in:st=0:d=0.4,afade=t=out:st={TOTAL - 1.2:.3f}:d=1.2[m];"
        "[m][key]sidechaincompress=threshold=0.035:ratio=5:attack=15:release=320:makeup=1[md];"
        "[v][md]amix=inputs=2:normalize=0:duration=first,"
        "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[out]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-i", testi, "-i", args.music,
                    "-filter_complex", graph, "-map", "[out]", "-ac", "2", "-ar", "48000", args.out], check=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
