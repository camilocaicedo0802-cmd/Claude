"""Reel 2 — "Your bathroom isn't the problem" (1080x1920, 30 fps). Times are output seconds.

v2: the silent stretch at the start of take IMG_7832 ("...vanity / But your shower") is cut, the no-voice
catalog beat is shorter, and every voice clip follows the previous one with an 80 ms gap.

Music (110 BPM, beat = 0.5392 s):
  segment A  video t = track t                 (0 .. FREEZE0, drop at 8.752)
  tape stop  FREEZE0 .. +0.45, then SFX only until SEGB (retro freeze)
  segment B  video t = track t + DB            (SEGB .. OUTRO, drop on the before/after REVEAL)
  outro      video OUTRO = track beat 64       (to the end)
"""
import glob, os
FPS = 30
W, H = 1080, 1920
P, B0 = 0.5391739901, 0.1250491308
GAP = 0.08
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

# ---------------------------------------------------------------- voice: (clip, src_in, src_out) placed back to back
_CLIPS = [
    ('IMG_7829.MOV', 0.80, 3.54),   # 0 Tulsa homeowners, your bathroom might not be outdated
    ('IMG_7830.MOV', 0.95, 2.98),   # 1 Your shower might be the problem.
    ('IMG_7831.MOV', 0.49, 4.42),   # 2 Think about it. You can change mirror, lighting, vanity
    ('IMG_7832.MOV', 0.84, 3.83),   # 3 But your shower still might look like it's from the 1990s   (0.08-0.84 was silence)
    ('IMG_7834.MOV', 0.59, 3.06),   # 4 The whole bathroom might feel outdated
    ('IMG_7835.MOV', 0.84, 3.90),   # 5 That's why we are focusing on shower transformations
    ('IMG_7836.MOV', 0.75, 2.20),   # 6 That makes a real difference
    ('IMG_7838.MOV', 1.69, 3.29),   # 7 From modern glass doors
    ('IMG_7839.MOV', 0.50, 2.16),   # 8 To beautiful finishes
    ('IMG_7840.MOV', 2.15, 5.84),   # 9 Before even think remodel the whole bathroom, just think about the shower
    ('IMG_7841.MOV', 0.84, 3.38),   # 10 We are West Home Improvement. Let's make it happen!
]
FREEZE_HOLD = 0.06          # extra time the freeze holds after "1990s" ends
CATALOG = 1.64              # no-voice beat for the shower catalog (no take of that line exists)
VOICE = []
t = 0.0
for k, (name, si, so) in enumerate(_CLIPS):
    VOICE.append((F(name), si, so, round(t, 3)))
    t += so - si + GAP
    if k == 8:
        CAT0 = round(t - GAP + 0.12, 3); t = CAT0 + CATALOG
VEND = round(VOICE[-1][3] + _CLIPS[-1][2] - _CLIPS[-1][1], 3)


def vt(k, src):
    """timeline time of source second `src` of voice clip k."""
    return round(VOICE[k][3] + src - VOICE[k][1], 3)


FREEZE0 = vt(3, 2.90)                 # "1990s"
FREEZE1 = round(vt(3, 3.83) + FREEZE_HOLD, 3)
SEGB = VOICE[4][3]                    # music segment B starts with "The whole bathroom"
REVEAL = vt(5, 3.12)                  # "transformations"
DB = round(REVEAL - (B0 + P * 16), 4)
END0 = round(VEND + 0.02, 3)


def ba(k):            # beat k in segment A (video time)
    return round(B0 + P * k, 4)


def bb(k):            # beat k in segment B (video time)
    return round(B0 + P * k + DB, 4)


OUTRO = bb(40) if bb(40) > END0 + 0.15 else bb(44)
DUR = round(OUTRO + 3.83, 2)


def sync(k, t0, t1, **kw):
    clip, si, so, tp = VOICE[k]
    return dict(src=clip, t0=t0, t1=t1, src_in=si + (t0 - tp), speed=1.0, person=True, **kw)


OLD = F('IMG_5220.mov')
SHOTS = [
    # 1 HOOK — Félix walking in, subtle push-in
    sync(0, 0.0, VOICE[1][3], grade='talk', zoom=[(0, 1.10), (1, 1.24)], cy=-0.02),
    # 2 Your shower...
    sync(1, VOICE[1][3], vt(1, 1.71), grade='talk', zoom=[(0, 1.16), (0.12, 1.06), (1, 1.12)], tin=('cut',)),
    # 3 ...might be the problem: dated fiberglass shower (photo)
    dict(src=PH + 'old_fiberglass.png', t0=vt(1, 1.71), t1=VOICE[2][3], src_in=0, speed=0, grade='old',
         zoom=[(0, 1.22), (0.15, 1.08), (1, 1.14)], dx=[(0, 0), (1, -30)], tin=('cut',)),
    # 4 Think about it. You can change...
    sync(2, VOICE[2][3], ba(12), grade='talk', zoom=[(0, 1.18), (0.1, 1.04), (1, 1.10)], tin=('whip', 'left', 0.2)),
    # 5-7 mirror / lighting / vanity
    dict(src=F('IMG_6232.MOV'), t0=ba(12), t1=ba(14), src_in=0.6, speed=1.1, grade='white',
         zoom=[(0, 1.14), (0.3, 1.04), (1, 1.06)], tin=('cut',)),
    dict(src=F('IMG_6234.MOV'), t0=ba(14), t1=ba(15), src_in=0.4, speed=1.2, grade='white', cy=-0.14,
         zoom=[(0, 1.42), (1, 1.32)], tin=('cut',)),
    dict(src=F('IMG_6239.MOV'), t0=ba(15), t1=ba(16), src_in=0.2, speed=1.4, grade='white',
         zoom=[(0, 1.16), (1, 1.06)], tin=('cut',)),
    # 8-9 the old shower (drop at beat 16)
    dict(src=OLD, t0=ba(16), t1=ba(18), src_in=6.3, speed=1.0, grade='old',
         zoom=[(0, 1.18), (0.15, 1.06), (1, 1.10)], tin=('zoom', 'in', 0.22)),
    dict(src=OLD, t0=ba(18), t1=FREEZE0, src_in=43.1, speed=1.0, grade='old',
         zoom=[(0, 1.06), (1, 1.12)], tin=('cut',)),
    # 10 RETRO FREEZE on "1990s"
    dict(src=OLD, t0=FREEZE0, t1=FREEZE1, src_in=43.1 + (FREEZE0 - ba(18)), speed=0.0, grade='retro', retro=True,
         zoom=[(0, 1.12), (0.08, 1.20), (1, 1.24)], tin=('cut',)),
    # 11 The whole bathroom might feel outdated
    dict(src=OLD, t0=FREEZE1, t1=vt(4, 2.10), src_in=0.4, speed=1.0, grade='old',
         zoom=[(0, 1.10), (1, 1.16)], tin=('flash', 'white', 0.24)),
    dict(src=PH + 'old_vanity.png', t0=vt(4, 2.10), t1=VOICE[5][3], src_in=0, speed=0, grade='old',
         zoom=[(0, 1.30), (0.2, 1.16), (1, 1.10)], tin=('cut',)),
    # 12 That's why we're focusing on...
    sync(5, VOICE[5][3], vt(5, 2.08), grade='talk', zoom=[(0, 1.16), (0.12, 1.04), (1, 1.08)], tin=('whip', 'up', 0.2)),
    # 13 BEFORE -> AFTER reveal (same bathroom)
    dict(src=F('IMG_7794.MOV'), t0=vt(5, 2.08), t1=bb(18), src_in=0.25,
         speed=[(0, 0.0), ((REVEAL - vt(5, 2.08)) / (bb(18) - vt(5, 2.08)), 0.0),
                ((REVEAL + 0.3 - vt(5, 2.08)) / (bb(18) - vt(5, 2.08)), 1.0), (1, 1.0)],
         grade='clean', before=PH + 'before.png', wipe=(REVEAL - 0.16, REVEAL + 0.20),
         zoom=[(0, 1.10), (0.5, 1.03), (1, 1.06)], tin=('zoom', 'in', 0.2)),
    # 14 That makes a real difference — Félix inside the new shower
    dict(src=F('IMG_7819.MOV'), t0=bb(18), t1=VOICE[7][3], src_in=1.75, speed=1.0, grade='clean', person=True,
         zoom=[(0, 1.12), (0.15, 1.02), (1, 1.06)], tin=('cut',)),
    # 15 modern glass doors
    dict(src=F('IMG_9058.MOV'), t0=VOICE[7][3], t1=bb(22), src_in=0.3, speed=0.9, grade='beige',
         zoom=[(0, 1.14), (0.3, 1.04), (1, 1.06)], tin=('whip', 'right', 0.2)),
    dict(src=F('IMG_9081.MOV'), t0=bb(22), t1=VOICE[8][3], src_in=0.5, speed=1.1, grade='beige', person=True,
         zoom=[(0, 1.10), (1, 1.04)], tin=('cut',)),
    # 16 beautiful finishes
    dict(src=F('IMG_7125.mov'), t0=VOICE[8][3], t1=bb(25), src_in=2.0, speed=1.0, grade='white',
         zoom=[(0, 1.14), (1, 1.04)], tin=('cut',)),
    dict(src=F('IMG_6236.MOV'), t0=bb(25), t1=bb(26), src_in=0.4, speed=0.6, grade='white',
         zoom=[(0, 1.12), (1, 1.04)], tin=('cut',)),
    dict(src=F('IMG_9076.MOV'), t0=bb(26), t1=CAT0, src_in=0.1, speed=0.9, grade='beige',
         zoom=[(0, 1.12), (1, 1.04)], tin=('cut',)),
    # 17 new shower catalog (no voice)
    dict(src=F('IMG_3698.MOV'), t0=CAT0, t1=round(CAT0 + 0.75, 3), src_in=3.4, speed=1.0, grade='office',
         zoom=[(0, 1.14), (0.2, 1.04), (1, 1.08)], tin=('whip', 'left', 0.2)),
    dict(src=F('IMG_3695.MOV'), t0=round(CAT0 + 0.75, 3), t1=VOICE[9][3], src_in=1.2, speed=1.0, grade='office',
         zoom=[(0, 1.08), (1, 1.14)], tin=('cut',)),
    # 18 Before even think remodel the whole bathroom,
    sync(9, VOICE[9][3], vt(9, 4.56), grade='talk', zoom=[(0, 1.16), (0.08, 1.04), (1, 1.10)], tin=('zoom', 'in', 0.2)),
    # 19 just think about the shower
    dict(src=F('IMG_0992.MOV'), t0=vt(9, 4.56), t1=VOICE[10][3], src_in=0.4, speed=0.8, grade='hlg',
         zoom=[(0, 1.18), (0.2, 1.05), (1, 1.08)], tin=('cut',)),
    # 20 We are West Home Improvement. Let's make it happen!
    sync(10, VOICE[10][3], END0, grade='talk', zoom=[(0, 1.14), (0.08, 1.04), (1, 1.12)], tin=('whip', 'up', 0.2)),
    # 21 END — best finished shower
    dict(src=F('IMG_7127.mov'), t0=END0, t1=DUR, src_in=7.0, speed=0.5, grade='hlg',
         zoom=[(0, 1.20), (0.06, 1.06), (1, 1.14)],
         dim_ramp=[(0, 0.0), (0.05, 0.2), (0.4, 0.28), (0.45, 0.45), (1, 0.5)], tin=('flash', 'white', 0.4)),
]

PHOTOS = {   # photo -> source (exif-rotated, center-cropped to 9:16)
    'old_fiberglass.png': 'IMG_9346.HEIC',
    'old_vanity.png': 'IMG_7503(1).HEIC',
    'before.png': 'IMG_9343.HEIC',
}

if __name__ == '__main__':
    for v in VOICE:
        print(os.path.basename(v[0]), v[1:])
    print('FREEZE', FREEZE0, FREEZE1, 'SEGB', SEGB, 'REVEAL', REVEAL, 'DB', DB, 'CAT0', CAT0, 'END0', END0,
          'OUTRO', OUTRO, 'DUR', DUR)
    for i, s in enumerate(SHOTS):
        assert s['t1'] > s['t0'] + 0.25, (i, s['t0'], s['t1'])
        if i:
            assert abs(SHOTS[i - 1]['t1'] - s['t0']) < 1e-6, (i, SHOTS[i - 1]['t1'], s['t0'])
        print(i, os.path.basename(s['src']), s['t0'], s['t1'], round(s['t1'] - s['t0'], 2))
