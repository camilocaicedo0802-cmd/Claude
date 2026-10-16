# Reel based on the Instagram reference

`reel_final.mp4`: 1080x1920, 30 fps, 12.4 s. Audio is copied unchanged from the reference video.

Every cut lands on the same frame as a cut in the reference, so the edit is synced to the audio.

| Output (s)  | Clip | Source range (s) |
|-------------|------|------------------|
| 0.00–5.73   | 1    | 6.00–11.73 (hand covers the lens at 5.73, like the reference) |
| 5.73–7.17   | 2    | 1.00–2.43 (0.2 s fade in from the dark frame) |
| 7.17–7.83   | 2    | 3.50–4.17 |
| 7.83–8.93   | 3    | 1.00–2.10 |
| 8.93–9.50   | 3    | 4.25–4.82 |
| 9.50–10.03  | 3    | 5.40–5.93 |
| 10.03–10.77 | 4    | 14.00–14.73 |
| 10.77–12.40 | 4    | 15.37–17.00 |

Color: each clip gets a white-balance and exposure correction (clip 1 less orange, clip 2 lifted shadows,
clip 4 green cast removed). All clips then share one look: soft curve, saturation 0.92, slight warmth.

`build.sh <dir>` rebuilds the reel. It expects `dl/v1..v4.mov` (the Drive clips) and `work/ref.mp4` (the reference) inside `<dir>`.
