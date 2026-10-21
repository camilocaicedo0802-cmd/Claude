# Pinktober — 15s promo (9:16)

Footage: Drive folder `1bXOMvKYINgF-yarOTtmk39fcLfpyEsAr` (9 event clips + `Pinktober.m4a` voiceover).
Style references: Dance Lovers Social reels (neon kinetic type, beat cuts, Tranqui Foundation end card).

- Voiceover: source 0.48–14.28 s ("Dance for a cause … survivors and thrivers"), placed at 0 s.
- Music: original salsa bed synthesized in `salsa.py` (190 BPM, 2-3 son clave, montuno, tumbao, congas,
  campana, güiro, brass mambo, timbal fill), ducked under the voice with `sidechaincompress`.
- Cuts land on the beat grid (15 shots, `SHOTS` in `render2.py`); transitions: flash, punch zoom, whip blur, RGB glitch.
- Type: Josefin Sans (dates/phrases), Archivo Black (impact words), Allura neon script (Pinktober, for a cause, wellness);
  highlights in pink. End card uses the Tranqui Foundation logo cropped from the reference's own end card.

```
python3 salsa.py $S/sfx
python3 render2.py $S $S/work/v2_noaudio.mp4
python3 mix2.py $S $S/work/pinktober_final.mp4
```
