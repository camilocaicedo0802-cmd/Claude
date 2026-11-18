"""Reel 3 — full bathroom remodel walkthrough with Félix & Peter (1080x1920, 30 fps). Times are output seconds.

v3 (client feedback): opens outside the house with Peter and Félix ("Hey Tulsa, we have another beautiful West Home
Improvement bathroom we just completed. Let's check it out."); the purple-room clip ("Are you ready to see something
nice?" + the walk through the door) is gone; hero B-roll in real slow motion (60 fps sources at half speed).

v4 (client feedback): the real before / demo photos of THIS bathroom (Drive folder "b roll de esta ducha") go where
Félix talks about it: the old stall on "remodel the shower area", the old vanity on "this space needs a lot of work",
the narrow doorway to the stall on "so it was really narrow to get into the shower" and the gutted room on "we demoed
the whole thing out" — then the finished shower on "to make a really open space".

The voice is built from the best fragments of the raw takes (no script); pauses are cut, pieces follow each
other with short gaps. Music: 104 BPM (beat 0.5769 s); its drop (track beat 32) lands on REVEAL.
"""
import glob, os
FPS = 30
W, H = 1080, 1920
P, B0 = 0.5769311385, 0.0385875471
ROOT = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel3/'
_all = None


def F(name):
    global _all
    if _all is None:
        _all = glob.glob(ROOT + 'dl/**/*', recursive=True) + glob.glob(ROOT + 'broll/**/*', recursive=True)
    m = sorted(p for p in _all if os.path.basename(p) == name)
    assert m, name
    if len(m) > 1:
        assert len({os.path.getsize(p) for p in m}) == 1, (name, m)
    return m[0]


PH = ROOT + 'photos/'
DOOR = 1.15          # no-voice walk-in through the door (music + whoosh)
TAIL = 1.6           # end card after the last line

# (take, src_in, src_out, gap_after)   — text in comments is what is said
_PIECES = [
    ('IMG_9014.MOV', 0.95, 2.24, 0.05),    # 0 initially the customers
    ('IMG_9014.MOV', 2.43, 3.91, 0.05),    # 1 they have the idea only
    ('IMG_9014.MOV', 4.24, 5.62, 0.08),    # 2 remodel the shower area,
    ('IMG_9014.MOV', 5.82, 6.23, 0.04),    # 3 but
    ('IMG_9014.MOV', 6.38, 11.97, round(3 * P - (11.97 - 11.40), 3)),   # 4 (gap = 3-beat reveal montage after 'whole thing') I mean this space needs a lot of work, so I gave them some suggestion and we ended up doing the whole thing.
    ('IMG_9009.MOV', 0.33, 1.98, DOOR),    # 5 Are you ready to see something nice?
    ('IMG_9014.MOV', 13.18, 14.81, 0.06),  # 6 There was a big wall here,
    ('IMG_9014.MOV', 17.90, 20.30, 0.08),  # 7 so it was really narrow to get into the shower.
    ('IMG_9014.MOV', 20.51, 24.02, 0.10),  # 8 We demoed the whole thing out to make a really open space.
    ('IMG_9014.MOV', 24.53, 26.58, 0.05),  # 9 With a new custom vanity
    ('IMG_9014.MOV', 27.53, 29.47, 0.10),  # 10 countertop to match the tile.
    ('IMG_9014.MOV', 31.23, 33.36, 0.10),  # 11 All the fixtures are completely new.
    ('IMG_9014.MOV', 36.82, 38.47, 0.08),  # 12 The shower is the masterpiece.
    ('IMG_9014.MOV', 40.03, 40.71, 0.04),  # 13 Classic
    ('IMG_9014.MOV', 41.24, 42.57, 0.05),  # 14 subway tile, but
    ('IMG_9014.MOV', 43.93, 46.16, 0.08),  # 15 make it look great like a luxury bathroom
    ('IMG_9014.MOV', 46.74, 47.71, 0.08),  # 16 custom niche,
    ('IMG_9014.MOV', 50.10, 50.69, 0.05),  # 17 a nice
    ('IMG_9014.MOV', 51.02, 52.24, 0.12),  # 18 glass custom door.
    ('IMG_9018.MOV', 0.14, 2.38, 0.08),    # 19 Alright Felix, we did it again. — Yes, sir.
    ('IMG_9020.MOV', 0.14, 2.10, TAIL),    # 20 You already know, call West Home Improvement.
    ('IMG_9039.MOV', 16.80, 20.84, 0.06),  # 21 (v3 intro, outside) Hey Tulsa, we have another beautiful West Home Improvement bathroom we just completed.
    ('IMG_9039.MOV', 22.88, 23.66, 0.10),  # 22 (v3 intro) Let's check it out.
]
# v3 order: the outside intro first; piece 5 (purple room, "Are you ready to see something nice?") and the door walk
# are dropped — piece 5 stays in the list with zero length at the start of piece 6 so the indices do not move.
ORDER = [21, 22, 0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
VOICE = [None] * len(_PIECES)
t = 0.0
for k in ORDER:
    name, si, so, gap = _PIECES[k]
    if k == 4:
        gap = round(3 * P - (11.97 - 11.40), 3)       # the 3-beat reveal montage after "the whole thing"
    VOICE[k] = (F(name), si, so, round(t, 3))
    t += so - si + gap
DUR = round(t, 2)
VOICE[5] = (F(_PIECES[5][0]), _PIECES[5][1], _PIECES[5][1], VOICE[6][3])


def vs(k):
    return VOICE[k][3]


def ve(k):
    return round(VOICE[k][3] + VOICE[k][2] - VOICE[k][1], 3)


def vt(k, src):
    return round(VOICE[k][3] + src - VOICE[k][1], 3)


REVEAL = vt(4, 11.40)                 # "...doing the WHOLE thing" — music drop
S0 = 32 - REVEAL / P                  # track beat at video t=0


def beat(k):                          # video time of track beat k
    return round((k - S0) * P, 4)


def sync(k, t0, t1, **kw):
    clip, si, so, tp = VOICE[k]
    return dict(src=clip, t0=t0, t1=t1, src_in=si + (t0 - tp), speed=1.0, person=True, **kw)


BR = lambda n: F(f'IMG_{n}.MOV')


def photo(name, t0, t1, zoom, **kw):
    """a before photo (HEIC from the client's folder, cropped 9:16 by extract_all.py) with a slow Ken Burns move."""
    return dict(src=PH + name + '.png', t0=t0, t1=t1, src_in=0.0, speed=0.0, grade='old', zoom=zoom, **kw)


SHOTS = [
    # INTRO — outside the house, Peter and Félix: "Hey Tulsa, we have another beautiful ... Let's check it out."
    sync(21, 0.0, vs(22), grade='talk', zoom=[(0, 1.02), (0.15, 1.08), (1, 1.12)], cy=0.02),
    sync(22, vs(22), vs(0), grade='talk', zoom=[(0, 1.18), (1, 1.22)], cy=0.0),
    # HOOK — Félix in the new bathroom: "Initially the customers, they had the idea only..."
    sync(0, vs(0), vs(1), grade='talk', zoom=[(0, 1.04), (0.12, 1.12), (1, 1.16)], cy=-0.02, tin=('whip', 'up', 0.2)),
    sync(1, vs(1), vs(2), grade='talk', zoom=[(0, 1.26), (1, 1.30)], cy=-0.04),
    # "...remodel the shower area," — v4: the OLD shower stall of this bathroom, through its doorway (before photo)
    photo('before_stall', vs(2), vs(3), zoom=[(0, 1.10), (1, 1.22)], cx=-0.04),
    sync(3, vs(3), vs(4), grade='talk', zoom=[(0, 1.30), (1, 1.32)], cy=-0.04),
    # "I mean this space / needs a lot of work." — v4: the old vanity and the old oak cabinets (before photos)
    photo('before_vanity', vs(4), vt(4, 7.42), zoom=[(0, 1.16), (1, 1.04)]),
    photo('before_cabinets', vt(4, 7.42), vt(4, 8.40), zoom=[(0, 1.04), (1, 1.14)]),
    sync(4, vt(4, 8.40), vt(4, 10.10), grade='talk', zoom=[(0, 1.26), (1, 1.30)], cy=-0.04),
    # "...and we ended up doing the whole thing" — quick reveal montage on the beat
    dict(src=BR(9023), t0=vt(4, 10.10), t1=REVEAL, src_in=0.2, speed=1.6, grade='white',
         zoom=[(0, 1.10), (1, 1.04)], tin=('zoom', 'in', 0.2)),
    dict(src=BR(9006), t0=REVEAL, t1=beat(33), src_in=0.3, speed=1.2, grade='white', zoom=[(0, 1.16), (1, 1.06)]),
    dict(src=BR(8994), t0=beat(33), t1=beat(34), src_in=0.2, speed=1.4, grade='white', zoom=[(0, 1.12), (1, 1.04)]),
    dict(src=BR(8982), t0=beat(34), t1=vs(5), src_in=0.5, speed=1.2, grade='white', zoom=[(0, 1.14), (1, 1.06)]),
    # (v3: the purple-room clip — "Are you ready to see something nice?" + the door walk — is removed)
    # "There was a big wall here, so it was really narrow to get into the shower."
    sync(6, vs(6), vs(7), grade='talk', zoom=[(0, 1.10), (1, 1.14)], tin=('zoom', 'in', 0.18)),
    # "so it was really narrow / to get into the shower." — v4: the narrow doorway to the old stall, then a punch-in
    photo('before_door', vs(7), vt(7, 19.14), zoom=[(0, 1.04), (1, 1.12)]),
    photo('before_door', vt(7, 19.14), vs(8), zoom=[(0, 1.55), (1, 1.66)], cx=-0.02, cy=0.02, tin=('zoom', 'in', 0.18)),
    # "We demoed / the whole thing out" — v4: the gutted room (demo photos), then the finished shower on
    # "to make a really open space"
    photo('demo_alcove', vs(8), vt(8, 21.27), zoom=[(0, 1.06), (1, 1.14)], tin=('whip', 'right', 0.2)),
    photo('demo_wall', vt(8, 21.27), vt(8, 22.10), zoom=[(0, 1.14), (1, 1.06)]),
    dict(src=BR(9023), t0=vt(8, 22.10), t1=vs(9), src_in=4.6, speed=1.0, grade='white', zoom=[(0, 1.10), (1, 1.04)],
         tin=('flash', 'white', 0.3)),
    # "With a new custom vanity countertop to match the tile."
    dict(src=BR(8994), t0=vs(9), t1=vt(9, 25.75), src_in=0.0, speed=1.1, grade='white', zoom=[(0, 1.12), (1, 1.04)],
         tin=('whip', 'left', 0.2)),
    dict(src=BR(8996), t0=vt(9, 25.75), t1=vs(10), src_in=0.8, speed=1.0, grade='white', zoom=[(0, 1.10), (1, 1.04)]),
    dict(src=BR(8999), t0=vs(10), t1=vs(11), src_in=0.3, speed=1.0, grade='white', zoom=[(0, 1.12), (1, 1.04)]),
    # "All the fixtures are completely new."
    dict(src=BR(8997), t0=vs(11), t1=vt(11, 32.40), src_in=0.4, speed=0.7, grade='white', zoom=[(0, 1.14), (1, 1.06)]),
    dict(src=BR(8980), t0=vt(11, 32.40), t1=vs(12), src_in=0.4, speed=1.0, grade='white', zoom=[(0, 1.12), (1, 1.04)]),
    # "The shower is the masterpiece."
    dict(src=BR(8985), t0=vs(12), t1=vs(13), src_in=0.5, speed=0.5, grade='white',      # real slow motion (60 fps)
         zoom=[(0, 1.28), (0.25, 1.08), (1, 1.12)], tin=('zoom', 'in', 0.2)),
    # "Classic subway tile, but"
    dict(src=BR(8981), t0=vs(13), t1=vs(15), src_in=4.6, speed=1.3, grade='white', zoom=[(0, 1.12), (1, 1.04)]),
    # "make it look great like a luxury bathroom" — Félix at the shower
    sync(15, vs(15), vs(16), grade='talk', zoom=[(0, 1.10), (1, 1.16)]),
    # "custom niche, a nice glass custom door."
    dict(src=BR(9006), t0=vs(16), t1=vs(17), src_in=13.0, speed=0.8, grade='white', zoom=[(0, 1.14), (1, 1.06)]),
    dict(src=BR(8983), t0=vs(17), t1=vs(19), src_in=0.6, speed=1.0, grade='white', zoom=[(0, 1.12), (1, 1.04)]),
    # "Alright Felix, we did it again." — "Yes, sir."  (outside, high five)
    sync(19, vs(19), vs(20), grade='talk', zoom=[(0, 1.10), (1, 1.14)], tin=('whip', 'up', 0.2)),
    # "You already know, call West Home Improvement."
    sync(20, vs(20), ve(20) + 0.04, grade='talk', zoom=[(0, 1.10), (1, 1.16)]),
    # END — hero shower
    dict(src=BR(8987), t0=ve(20) + 0.04, t1=DUR, src_in=0.5, speed=0.5, grade='white',   # real slow motion (60 fps)
         zoom=[(0, 1.16), (0.1, 1.04), (1, 1.10)], dim_ramp=[(0, 0.0), (0.15, 0.32), (1, 0.4)], tin=('flash', 'white', 0.3)),
]
# v4: before / demo photos of this bathroom — out png: (HEIC, horizontal centre of the 9:16 crop)
PHOTOS = {
    'before_stall.png': ('IMG_6529.HEIC', 0.375),
    'before_vanity.png': ('IMG_7503.HEIC', 0.5),
    'before_cabinets.png': ('IMG_7512.HEIC', 0.5),
    'before_door.png': ('IMG_6528.HEIC', 0.375),
    'demo_alcove.png': ('IMG_7573.HEIC', 0.5),
    'demo_wall.png': ('IMG_7650.HEIC', 0.5),
}

if __name__ == '__main__':
    for k, v in enumerate(VOICE):
        print(k, os.path.basename(v[0]), v[1:], ve(k))
    print('REVEAL', REVEAL, 'S0', round(S0, 3), 'DUR', DUR)
    for i, s in enumerate(SHOTS):
        assert s['t1'] > s['t0'] + 0.2, (i, s['t0'], s['t1'])
        if i:
            assert abs(SHOTS[i - 1]['t1'] - s['t0']) < 1e-6, (i, SHOTS[i - 1]['t1'], s['t0'])
        print(i, os.path.basename(s['src']), s['t0'], s['t1'], round(s['t1'] - s['t0'], 2))
