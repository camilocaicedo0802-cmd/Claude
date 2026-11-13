"""Reel 2 — "Your bathroom isn't the problem" (1080x1920, 30 fps). Times are output seconds.

Music (110 BPM, beat = 0.5392 s):
  segment A  video t = track t                      (0 .. 11.76, drop at 8.752)
  tape stop  11.76 .. 12.20, silence to 12.85 (retro freeze)
  segment B  video t = track t + 8.928              (12.85 .. 32.77, drop at 17.68 = before/after reveal)
  outro      video 32.77 = track 34.63 (beat 64)    (to the end)
"""
import glob, os
FPS = 30
W, H = 1080, 1920
DUR = 36.4
P, B0 = 0.5391739901, 0.1250491308
DB = 8.928                          # segment B offset
REVEAL = 17.68


def ba(k):            # beat k in segment A (video time)
    return round(B0 + P * k, 4)


def bb(k):            # beat k in segment B (video time)
    return round(B0 + P * k + DB, 4)


ROOT = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel2/'
_all = None


def F(name):
    global _all
    if _all is None:
        _all = glob.glob(ROOT + 'dl/**/*', recursive=True)
    m = sorted(p for p in _all if os.path.basename(p) == name)
    assert m, name
    if len(m) > 1:   # identical copies in two folders
        assert len({os.path.getsize(p) for p in m}) == 1, (name, m)
    return m[0]


PH = ROOT + 'photos/'

# ---------------------------------------------------------------- voice: (clip, src_in, src_out, t_place)
VOICE = [
    (F('IMG_7829.MOV'), 0.80, 3.54, 0.00),    # Tulsa homeowners, your bathroom might not be outdated
    (F('IMG_7830.MOV'), 0.95, 2.98, 2.82),    # Your shower might be the problem.
    (F('IMG_7831.MOV'), 0.49, 4.42, 4.93),    # Think about it. You can change mirror, lighting, vanity
    (F('IMG_7832.MOV'), 0.08, 3.83, 8.94),    # But your shower still might look like it's from the 1990s
    (F('IMG_7834.MOV'), 0.59, 3.06, 12.85),   # The whole bathroom might feel outdated
    (F('IMG_7835.MOV'), 0.84, 3.90, 15.40),   # That's why we are focusing on shower transformations
    (F('IMG_7836.MOV'), 0.75, 2.20, 18.54),   # That makes a real difference
    (F('IMG_7838.MOV'), 1.69, 3.29, 20.07),   # From modern glass doors
    (F('IMG_7839.MOV'), 0.50, 2.16, 21.75),   # To beautiful finishes
    (F('IMG_7840.MOV'), 2.15, 5.84, 26.00),   # Before even think remodel the whole bathroom, just think about the shower
    (F('IMG_7841.MOV'), 0.84, 3.38, 29.79),   # We are West Home Improvement. Let's make it happen!
]


def sync(k, t0, t1, **kw):
    clip, si, so, tp = VOICE[k]
    return dict(src=clip, t0=t0, t1=t1, src_in=si + (t0 - tp), speed=1.0, **kw)


OLD = F('IMG_5220.mov')
SHOTS = [
    # 1 HOOK — Félix walking in, subtle push-in
    sync(0, 0.0, 2.82, grade='talk', zoom=[(0, 1.10), (1, 1.24)], cy=-0.02),
    # 2 Your shower...
    sync(1, 2.82, ba(7), grade='talk', zoom=[(0, 1.16), (0.12, 1.06), (1, 1.12)], tin=('cut',)),
    # 3 ...might be the problem: dated fiberglass shower (photo, slow push + drift)
    dict(src=PH + 'old_fiberglass.png', t0=ba(7), t1=4.93, src_in=0, speed=0, grade='old',
         zoom=[(0, 1.22), (0.15, 1.08), (1, 1.14)], dx=[(0, 0), (1, -30)], tin=('cut',)),
    # 4 Think about it. You can change...
    sync(2, 4.93, ba(12), grade='talk', zoom=[(0, 1.18), (0.1, 1.04), (1, 1.10)], tin=('whip', 'left', 0.2)),
    # 5-7 mirror / lighting / vanity
    dict(src=F('IMG_6232.MOV'), t0=ba(12), t1=ba(14), src_in=0.6, speed=1.1, grade='white',
         zoom=[(0, 1.14), (0.3, 1.04), (1, 1.06)], tin=('cut',)),
    dict(src=F('IMG_6234.MOV'), t0=ba(14), t1=ba(15), src_in=0.4, speed=1.2, grade='white', cy=-0.14,
         zoom=[(0, 1.42), (1, 1.32)], tin=('cut',)),
    dict(src=F('IMG_6239.MOV'), t0=ba(15), t1=ba(16), src_in=0.2, speed=1.4, grade='white',
         zoom=[(0, 1.16), (1, 1.06)], tin=('cut',)),
    # 8-9 the old shower (drop at beat 16)
    dict(src=OLD, t0=ba(16), t1=ba(19), src_in=6.3, speed=1.0, grade='old',
         zoom=[(0, 1.18), (0.15, 1.06), (1, 1.10)], tin=('zoom', 'in', 0.22)),
    dict(src=OLD, t0=ba(19), t1=11.76, src_in=43.0, speed=1.0, grade='old',
         zoom=[(0, 1.06), (1, 1.12)], tin=('cut',)),
    # 10 RETRO FREEZE on "1990s"
    dict(src=OLD, t0=11.76, t1=12.85, src_in=44.4, speed=0.0, grade='retro', retro=True,
         zoom=[(0, 1.12), (0.08, 1.20), (1, 1.24)], tin=('cut',)),
    # 11 The whole bathroom might feel outdated
    dict(src=OLD, t0=12.85, t1=14.35, src_in=0.4, speed=1.0, grade='old',
         zoom=[(0, 1.10), (1, 1.16)], tin=('flash', 'white', 0.3)),
    dict(src=PH + 'old_vanity.png', t0=14.35, t1=15.40, src_in=0, speed=0, grade='old',
         zoom=[(0, 1.30), (0.2, 1.16), (1, 1.10)], tin=('cut',)),
    # 12 That's why we're focusing on...
    sync(5, 15.40, 16.62, grade='talk', zoom=[(0, 1.16), (0.12, 1.04), (1, 1.08)], tin=('whip', 'up', 0.2)),
    # 13 BEFORE -> AFTER reveal (same bathroom, same angle)
    dict(src=F('IMG_7794.MOV'), t0=16.62, t1=bb(18), src_in=0.25, speed=[(0, 0.0), (0.5, 0.0), (0.62, 1.0), (1, 1.0)],
         grade='clean', before=PH + 'before.png', wipe=(REVEAL - 0.16, REVEAL + 0.20),
         zoom=[(0, 1.10), (0.5, 1.03), (1, 1.06)], tin=('zoom', 'in', 0.2)),
    # 14 That makes a real difference — Félix inside the new shower
    dict(src=F('IMG_7819.MOV'), t0=bb(18), t1=20.07, src_in=1.75, speed=1.0, grade='clean',
         zoom=[(0, 1.12), (0.15, 1.02), (1, 1.06)], tin=('cut',)),
    # 15 modern glass doors
    dict(src=F('IMG_9058.MOV'), t0=20.07, t1=bb(22), src_in=0.3, speed=0.9, grade='beige',
         zoom=[(0, 1.14), (0.3, 1.04), (1, 1.06)], tin=('whip', 'right', 0.2)),
    dict(src=F('IMG_9081.MOV'), t0=bb(22), t1=21.75, src_in=0.5, speed=1.1, grade='beige',
         zoom=[(0, 1.10), (1, 1.04)], tin=('cut',)),
    # 16 beautiful finishes
    dict(src=F('IMG_7125.mov'), t0=21.75, t1=bb(25), src_in=2.0, speed=1.0, grade='white',
         zoom=[(0, 1.14), (1, 1.04)], tin=('cut',)),
    dict(src=F('IMG_6236.MOV'), t0=bb(25), t1=bb(26), src_in=0.4, speed=0.6, grade='white',
         zoom=[(0, 1.12), (1, 1.04)], tin=('cut',)),
    dict(src=F('IMG_9076.MOV'), t0=bb(26), t1=bb(27), src_in=0.1, speed=0.9, grade='beige',
         zoom=[(0, 1.12), (1, 1.04)], tin=('cut',)),
    # 17 new shower catalog
    dict(src=F('IMG_3698.MOV'), t0=bb(27), t1=bb(29), src_in=3.2, speed=1.0, grade='office',
         zoom=[(0, 1.14), (0.2, 1.04), (1, 1.08)], tin=('whip', 'left', 0.2)),
    dict(src=F('IMG_3695.MOV'), t0=bb(29), t1=26.00, src_in=1.0, speed=1.0, grade='office',
         zoom=[(0, 1.08), (1, 1.16)], tin=('cut',)),
    # 18 Before even think remodel the whole bathroom,
    sync(9, 26.00, 28.40, grade='talk', zoom=[(0, 1.16), (0.08, 1.04), (1, 1.10)], tin=('zoom', 'in', 0.2)),
    # 19 just think about the shower
    dict(src=F('IMG_0992.MOV'), t0=28.40, t1=29.79, src_in=0.4, speed=0.8, grade='hlg',
         zoom=[(0, 1.18), (0.2, 1.05), (1, 1.08)], tin=('cut',)),
    # 20 We are West Home Improvement. Let's make it happen!
    sync(10, 29.79, 32.33, grade='talk', zoom=[(0, 1.14), (0.08, 1.04), (1, 1.12)], tin=('whip', 'up', 0.2)),
    # 21 END — best finished shower
    dict(src=F('IMG_7127.mov'), t0=32.33, t1=DUR, src_in=7.0, speed=0.5, grade='hlg',
         zoom=[(0, 1.20), (0.06, 1.06), (1, 1.14)],
         dim_ramp=[(0, 0.0), (0.05, 0.2), (0.4, 0.28), (0.45, 0.45), (1, 0.5)], tin=('flash', 'white', 0.4)),
]

PHOTOS = {   # photo -> source (exif-rotated, center-cropped to 9:16)
    'old_fiberglass.png': 'IMG_9346.HEIC',
    'old_vanity.png': 'IMG_7503(1).HEIC',
    'before.png': 'IMG_9343.HEIC',
}
