"""Reel 4 — Meta Ads: jacuzzi tub turned into a massive walk-in shower (1080x1920, 30 fps). Times are output seconds.

Voice: Peter West (outside, by the truck), best fragments, pauses cut. B-roll leads; Peter on camera only at the
open, mid-story and the CTA. Music: the 100 BPM original track of reel 1 (beat 0.6 s); its break (track beats 30-31)
sits under "into the new shower area" and the drop (track beat 32) lands on REVEAL ("creating this massive...").
"""
import glob, os
FPS = 30
W, H = 1080, 1920
P, B0 = 0.6000508825, 0.0348587766
ROOT = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel4/'
_all = None


def F(name):
    global _all
    if _all is None:
        _all = glob.glob(ROOT + 'dl/**/*', recursive=True)
    m = sorted(p for p in _all if os.path.basename(p) == name)
    assert m, name
    if len(m) > 1:
        assert len({os.path.getsize(p) for p in m}) == 1, (name, m)
    return m[0]


PH = ROOT + 'photos/'
END = 2.6            # end card after "Reach out today."

# (take, src_in, src_out, gap_after)
_PIECES = [
    ('IMG_9119.MOV', 5.36, 8.04, 0.10),    # 0 This customer came at us with a couple of problems.
    ('IMG_9119.MOV', 8.53, 11.58, 0.10),   # 1 One, they needed to remodel an existing shower,
    ('IMG_9119.MOV', 11.84, 16.80, 0.12),  # 2 and two, they had a jacuzzi tub that was not usable space anymore.
    ('IMG_9119.MOV', 17.72, 25.33, 0.10),  # 3 We suggested to turn the jacuzzi tub area into the new shower area, creating this massive, beautiful new shower,
    ('IMG_9119.MOV', 25.70, 29.95, 0.12),  # 4 and turn the old shower area into a storage closet,
    ('IMG_9119.MOV', 31.66, 34.77, 0.06),  # 5 completely transforming their space, giving them
    ('IMG_9119.MOV', 35.03, 35.94, 0.06),  # 6 functionality
    ('IMG_9119.MOV', 36.42, 38.85, 0.14),  # 7 and features that they really wanted.
    ('IMG_9121.MOV', 0.24, 3.40, 0.10),    # 8 Remember, our shower remodels start at $9,800.
    ('IMG_9122.MOV', 1.53, 2.36, END),     # 9 Reach out today.
]
VOICE = []
t = 0.0
for name, si, so, gap in _PIECES:
    VOICE.append((F(name), si, so, round(t, 3)))
    t += so - si + gap
DUR = round(t, 2)


def vs(k):
    return VOICE[k][3]


def ve(k):
    return round(VOICE[k][3] + VOICE[k][2] - VOICE[k][1], 3)


def vt(k, src):
    return round(VOICE[k][3] + src - VOICE[k][1], 3)


REVEAL = vt(3, 22.28)                 # "creating this massive, beautiful new shower"
MASSIVE = 16.50                       # "massive" (word start - 0.05, from the transcript)
TS0 = (B0 + 32 * P) - REVEAL          # track time at video t = 0


def beat(k):                          # video time of track beat k
    return round(B0 + k * P - TS0, 4)


def sync(k, t0, t1, **kw):
    clip, si, so, tp = VOICE[k]
    return dict(src=clip, t0=t0, t1=t1, src_in=si + (t0 - tp), speed=1.0, person=True, **kw)


BR = lambda n: F(f'IMG_{n}.MOV')
PHOTO = lambda name: PH + name
SHOTS = [
    # HOOK — Peter on camera: "This customer came at us..."
    sync(0, 0.0, vt(0, 6.62), grade='talk', zoom=[(0, 1.06), (0.15, 1.14), (1, 1.18)], cy=-0.02),
    # "...with a couple of problems." — the dated bathroom
    dict(src=PHOTO('old_vanity.png'), t0=vt(0, 6.62), t1=vs(1), src_in=0, speed=0, grade='old',
         zoom=[(0, 1.30), (0.2, 1.14), (1, 1.10)], tin=('zoom', 'in', 0.18)),
    # "One, they needed to remodel an existing shower" — the old shower stall
    dict(src=PHOTO('old_room.png'), t0=vs(1), t1=vt(1, 9.95), src_in=0, speed=0, grade='old',
         zoom=[(0, 1.10), (1, 1.18)], tin=('whip', 'left', 0.2)),
    dict(src=PHOTO('old_room.png'), t0=vt(1, 9.95), t1=vs(2), src_in=0, speed=0, grade='old', cx=-0.11, cy=-0.01,
         zoom=[(0, 1.95), (1, 2.15)]),          # punch-in on the old stall through the doorway
    # "and two, they had a jacuzzi tub" — Peter; "that was not usable space anymore" — the old room
    sync(2, vs(2), vt(2, 13.80), grade='talk', zoom=[(0, 1.20), (1, 1.24)], cy=-0.04),
    dict(src=PHOTO('old_shower.png'), t0=vt(2, 13.80), t1=vt(2, 15.25), src_in=0, speed=0, grade='old',
         zoom=[(0, 1.12), (1, 1.22)], tin=('zoom', 'in', 0.18)),
    dict(src=PHOTO('old_counter.png'), t0=vt(2, 15.25), t1=vs(3), src_in=0, speed=0, grade='old',
         zoom=[(0, 1.22), (1, 1.10)]),
    # "We suggested to turn the jacuzzi tub area into the new shower area," — the process
    dict(src=PHOTO('demo.png'), t0=vs(3), t1=vt(3, 19.30), src_in=0, speed=0, grade='old',
         zoom=[(0, 1.10), (1, 1.20)], tin=('whip', 'up', 0.2)),
    dict(src=PHOTO('gutted.png'), t0=vt(3, 19.30), t1=vt(3, 20.95), src_in=0, speed=0, grade='old',
         zoom=[(0, 1.18), (1, 1.08)]),
    dict(src=PHOTO('build.png'), t0=vt(3, 20.95), t1=REVEAL, src_in=0, speed=0, grade='old',
         zoom=[(0, 1.10), (1, 1.22)]),
    # "creating this" — Félix slides the glass door open (drop); "massive, beautiful new shower" — the hero shot
    dict(src=F('IMG_9046.MOV'), t0=REVEAL, t1=MASSIVE, src_in=1.2, speed=[(0, 1.4), (1, 1.1)], grade='beige',
         person=True, zoom=[(0, 1.16), (0.3, 1.06), (1, 1.08)], tin=('flash', 'white', 0.3)),
    dict(src=BR(9040), t0=MASSIVE, t1=vs(4), src_in=0.6, speed=1.0, grade='beige', zoom=[(0, 1.16), (0.12, 1.06), (1, 1.02)]),
    # "and turn the old shower area into a storage closet" — Félix opens the closet
    dict(src=F('IMG_9084.MOV'), t0=vs(4), t1=vt(4, 27.90), src_in=0.2, speed=[(0, 1.0), (0.5, 1.5), (1, 1.6)], grade='white',
         person=True, zoom=[(0, 1.10), (1, 1.04)], tin=('whip', 'right', 0.2)),
    dict(src=BR(9044), t0=vt(4, 27.90), t1=vs(5), src_in=0.4, speed=1.2, grade='white', zoom=[(0, 1.14), (1, 1.04)]),
    # "completely transforming their space, giving them" — sweep of the shower
    dict(src=BR(9054), t0=vs(5), t1=vs(6), src_in=1.0, speed=1.5, grade='beige', zoom=[(0, 1.08), (1, 1.04)],
         tin=('zoom', 'in', 0.18)),
    # "functionality" — Félix sits on the built-in bench
    dict(src=F('IMG_9048.MOV'), t0=vs(6), t1=vs(7), src_in=3.6, speed=1.6, grade='beige', person=True,
         zoom=[(0, 1.12), (1, 1.06)]),
    # "and features that they really wanted." — feature montage on the beat
    dict(src=BR(9079), t0=vs(7), t1=vt(7, 37.05), src_in=0.4, speed=1.0, grade='beige', zoom=[(0, 1.12), (1, 1.04)]),
    dict(src=BR(9080), t0=vt(7, 37.05), t1=vt(7, 37.65), src_in=1.6, speed=1.0, grade='beige', zoom=[(0, 1.12), (1, 1.04)]),
    dict(src=BR(9076), t0=vt(7, 37.65), t1=vt(7, 38.25), src_in=0.1, speed=1.0, grade='beige', zoom=[(0, 1.12), (1, 1.04)]),
    dict(src=BR(9074), t0=vt(7, 38.25), t1=vs(8), src_in=1.0, speed=1.0, grade='beige', zoom=[(0, 1.12), (1, 1.04)]),
    # "Remember, our shower remodels start at $9,800." — Peter, then the hero shower with the price
    sync(8, vs(8), vt(8, 1.25), grade='talk', zoom=[(0, 1.14), (1, 1.18)], cy=-0.02, tin=('whip', 'up', 0.2)),
    dict(src=BR(9058), t0=vt(8, 1.25), t1=vs(9), src_in=0.3, speed=0.8, grade='beige', dim=0.32,
         zoom=[(0, 1.18), (0.15, 1.06), (1, 1.10)], tin=('zoom', 'in', 0.18)),
    # "Reach out today." — Peter
    sync(9, vs(9), ve(9) + 0.05, grade='talk', zoom=[(0, 1.12), (1, 1.16)], cy=-0.02),
    # END card — the finished shower, logo, CTA
    dict(src=BR(9041), t0=ve(9) + 0.05, t1=DUR, src_in=0.2, speed=0.7, grade='beige',
         zoom=[(0, 1.16), (0.1, 1.04), (1, 1.10)], dim_ramp=[(0, 0.0), (0.12, 0.38), (1, 0.44)], tin=('flash', 'white', 0.3)),
]
PHOTOS = {   # photo -> source (exif-rotated, center-cropped to 9:16)
    'old_vanity.png': 'IMG_7503(1).HEIC',
    'old_shower.png': 'IMG_6529.HEIC',
    'old_room.png': 'IMG_6528.HEIC',
    'old_counter.png': 'IMG_7512.HEIC',
    'demo.png': 'IMG_7575(1).HEIC',
    'gutted.png': 'IMG_7650.HEIC',
    'build.png': 'IMG_7649.HEIC',
}

if __name__ == '__main__':
    for k, v in enumerate(VOICE):
        print(k, os.path.basename(v[0]), v[1:], ve(k))
    print('REVEAL', REVEAL, 'TS0', round(TS0, 3), 'DUR', DUR, 'beat62', beat(62), 'beat64', beat(64))
    for i, s in enumerate(SHOTS):
        assert s['t1'] > s['t0'] + 0.2, (i, s['t0'], s['t1'])
        if i:
            assert abs(SHOTS[i - 1]['t1'] - s['t0']) < 1e-6, (i, SHOTS[i - 1]['t1'], s['t0'])
        print(i, os.path.basename(s['src']), s['t0'], s['t1'], round(s['t1'] - s['t0'], 2))
