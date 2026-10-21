# Ornaments — organic 15s vertical edit

Raw: `ORNAMENTS.MOV` (Drive id `1o2Ll53Ff43_x0M4G6Kz43wMSY-Osffgy`). Style reference: Lumily talking-head reel
(cream boxed hook title, small white subs, big cream keyword above the head, jump-cut zooms).

Cut (source seconds, any mention of "June" removed):

| # | Source | Line |
|---|--------|------|
| 1 | 5.73–7.85 | when something this beautiful just arrived |
| 2 | 8.60–9.46 | I have to share it |
| 3 | 25.76–30.50 | these are ceramic ornaments, each hand painted by Cecilia in Mexico |
| 4 | 13.42–15.54 | each one is one of a kind |
| 5 | 33.62–36.60 | I'm gonna start hanging these on every single gift bag |
| 6 | 44.72–46.74 | I can't decide which one's my favorite |
| 7 | 56.76–57.44 | get one |

Played at 1.033x → 15.0s. The MOV's audio track has internal gaps, so all timings are on an audio track
re-aligned to the video clock (`aresample=async=1:first_pts=0`), not on a plain extraction.

Pipeline (`$S` = working dir with `raw/ORNAMENTS.MOV` and `fonts/` from `@fontsource/outfit` + `@fontsource/tiktok-sans`):

```
ffmpeg -i $S/raw/ORNAMENTS.MOV -map 0:a -af "aresample=async=1:first_pts=0" -ar 48000 $S/work/full48.wav
python3 audio_synth.py $S/sfx          # soft music bed + whoosh/pop/ding/sparkle, all synthesized
python3 render.py $S $S/work/video_noaudio.mp4   # add 'cached' to reuse work/mattes.npy
python3 mix.py $S $S/work/final.mp4
```

Big keywords sit **behind** the speaker: MODNet (`Xenova/modnet` ONNX, see `matte.py`) mattes every frame, and
`place_keyword` picks the largest size/position where the upper half of every letter stays clear of her for
the whole time the word is on screen, so no keyword ever covers her face.
