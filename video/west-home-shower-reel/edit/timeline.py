"""Edit decisions for the West Home Improvement shower reel (1080x1920, 30 fps).

Times are output seconds. Music: 100 BPM, beat k at 0.035 + 0.6*k (after the bar splice at 24.035).
"""
FPS = 30
W, H = 1080, 1920
DUR = 32.6
BEAT0, BEAT = 0.035, 0.6


def beat(k):
    return round(BEAT0 + BEAT * k, 4)


RAW = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/west/raw/'
P1 = RAW + 'p1/Después/Videos/'
P2 = RAW + 'p2/'
P3 = RAW + 'p3/Después/Videos/'
P4 = RAW + 'p4/Después/Videos/'
P4F = RAW + 'p4/Después/Videos de Félix/'

# ---------------------------------------------------------------- voice
# (clip file, src_in, src_out, t_place)
VOICE = [
    (P2 + 'IMG_9096.MOV', 0.38, 4.30, 0.00),   # Tulsa homeowners thinking about remodeling your shower? Let us help you.
    (P2 + 'IMG_9103.MOV', 0.08, 3.08, 4.02),   # At West Home Improvement, we guide you through the entire process.
    (P2 + 'IMG_9106.MOV', 0.00, 3.47, 7.23),   # We'll help you choose the right tile, fixtures, and finishes.
    (P2 + 'IMG_9111.MOV', 1.42, 6.48, 13.20),  # And you know what? The best part? We handle everything, from demolition to the final installation.
    (P2 + 'IMG_9112.MOV', 0.40, 3.58, 18.32),  # With shower remodels starting at $9,800,
    (P2 + 'IMG_9112.MOV', 4.42, 6.70, 21.72),  # your dream shower is closer than you might think.
    (P2 + 'IMG_9116.MOV', 0.12, 1.62, 24.22),  # Reach out to get started.
]

# ---------------------------------------------------------------- shots
# Each shot: dict(src, t0, t1, src_in, speed=[(u, s), ...] or float, zoom=[(u, z)], dx/dy pan in px,
#   grade preset, tin=transition into this shot at t0)
# sync shots: src = t - t0 + src_in (speed 1)

def sync(clip, t0, t1, t_place, src_place, **kw):
    """Shot whose picture stays in sync with a voice clip placed at t_place (src_place)."""
    return dict(src=clip, t0=t0, t1=t1, src_in=src_place + (t0 - t_place), speed=1.0, **kw)


SHOTS = [
    # 1 HOOK: both walking to camera, quick punch-in then slow push
    sync(P2 + 'IMG_9096.MOV', 0.0, beat(6.5), 0.00, 0.38, grade='talk',
         zoom=[(0, 1.06), (0.1, 1.2), (1, 1.28)], cy=-0.03),
    # 2 At West Home Improvement (walking along the branded truck)
    sync(P2 + 'IMG_9103.MOV', beat(6.5), beat(9), 4.02, 0.08, grade='talk',
         zoom=[(0, 1.12), (0.12, 1.02), (1, 1.07)], tin=('whip', 'left', 0.2)),
    # 3 ...we guide you through the entire process -> walk into the beige shower (speed ramp)
    dict(src=P1 + 'IMG_9043.MOV', t0=beat(9), t1=beat(12), src_in=1.1,
         speed=[(0, 2.4), (0.25, 0.7), (0.7, 0.7), (1, 2.6)], zoom=[(0, 1.18), (0.2, 1.04), (1, 1.06)],
         grade='beige', tin=('zoom', 'in', 0.24)),
    # 4 We'll help you choose the right...
    sync(P2 + 'IMG_9106.MOV', beat(12), beat(14), 7.23, 0.00, grade='talk',
         zoom=[(0, 1.10), (0.15, 1.02), (1, 1.06)], tin=('cut',)),
    # 5 tile
    dict(src=P4 + 'IMG_7801.MOV', t0=beat(14), t1=beat(15.5), src_in=0.5, speed=0.9,
         zoom=[(0, 1.16), (0.3, 1.05), (1, 1.02)], grade='grey', tin=('cut',)),
    # 6 fixtures: black faucet running water, slow motion
    dict(src=P3 + 'IMG_8997.MOV', t0=beat(15.5), t1=beat(17), src_in=0.15, speed=0.6,
         zoom=[(0, 1.15), (0.3, 1.05), (1, 1.03)], grade='white', tin=('cut',)),
    # 7 finishes: marble bench
    dict(src=P1 + 'IMG_9077.MOV', t0=beat(17), t1=beat(18), src_in=0.6, speed=1.0,
         zoom=[(0, 1.15), (0.3, 1.05), (1, 1.03)], grade='beige', tin=('cut',)),
    # 8-11 YOUR HOME. YOUR STYLE. (three styles, cuts on the beat)
    dict(src=P1 + 'IMG_9054.MOV', t0=beat(18), t1=beat(19), src_in=2.2, speed=1.3,
         zoom=[(0, 1.12), (0.3, 1.03), (1, 1.05)], grade='beige', tin=('whip', 'up', 0.2)),
    dict(src=P3 + 'IMG_8981.MOV', t0=beat(19), t1=beat(20), src_in=0.2, speed=1.3,
         zoom=[(0, 1.12), (0.3, 1.03), (1, 1.05)], grade='white', tin=('cut',)),
    dict(src=P4 + 'IMG_7799.MOV', t0=beat(20), t1=beat(21), src_in=0.3, speed=1.3,
         zoom=[(0, 1.12), (0.3, 1.03), (1, 1.05)], grade='grey', tin=('cut',)),
    dict(src=P3 + 'IMG_8984.MOV', t0=beat(21), t1=beat(22), src_in=0.4, speed=1.3,
         zoom=[(0, 1.12), (0.3, 1.03), (1, 1.06)], grade='white', tin=('cut',)),
    # 12 And you know what? The best part? WE HANDLE EVERYTHING
    sync(P2 + 'IMG_9111.MOV', beat(22), beat(26), 13.20, 1.42, grade='talk',
         zoom=[(0, 1.14), (0.06, 1.03), (0.5, 1.05), (0.53, 1.13), (1, 1.16)], tin=('spin', 'cw', 0.3)),
    # 13-20 from demolition to the final installation: half-beat montage
    dict(src=P1 + 'IMG_9081.MOV', t0=beat(26), t1=beat(26.5), src_in=0.15, speed=1.8,
         zoom=[(0, 1.1), (1, 1.02)], grade='beige', tin=('cut',)),
    dict(src=P4F + 'IMG_7818.MOV', t0=beat(26.5), t1=beat(27), src_in=10.2, speed=1.8,
         zoom=[(0, 1.1), (1, 1.02)], grade='grey', tin=('cut',)),
    dict(src=P4 + 'IMG_7804.MOV', t0=beat(27), t1=beat(27.5), src_in=0.2, speed=1.8,
         zoom=[(0, 1.1), (1, 1.02)], grade='grey', tin=('cut',)),
    dict(src=P1 + 'IMG_9076.MOV', t0=beat(27.5), t1=beat(28), src_in=0.15, speed=1.2,
         zoom=[(0, 1.1), (1, 1.02)], grade='beige', tin=('cut',)),
    dict(src=P4 + 'IMG_7802.MOV', t0=beat(28), t1=beat(28.5), src_in=0.4, speed=1.8,
         zoom=[(0, 1.1), (1, 1.02)], grade='grey', tin=('cut',)),
    dict(src=P1 + 'IMG_9074.MOV', t0=beat(28.5), t1=beat(29), src_in=0.5, speed=1.8,
         zoom=[(0, 1.1), (1, 1.02)], grade='beige', tin=('cut',)),
    dict(src=P1 + 'IMG_9080.MOV', t0=beat(29), t1=beat(29.5), src_in=1.4, speed=1.8,
         zoom=[(0, 1.1), (1, 1.02)], grade='beige', tin=('cut',)),
    dict(src=P4F + 'IMG_7819.MOV', t0=beat(29.5), t1=beat(30), src_in=3.0, speed=1.0,
         zoom=[(0, 1.12), (1, 1.04)], grade='grey', tin=('cut',)),
    # 21 With shower remodels... (music break)
    sync(P2 + 'IMG_9112.MOV', beat(30), beat(32), 18.32, 0.40, grade='talk',
         zoom=[(0, 1.12), (0.1, 1.03), (1, 1.10)], tin=('whip', 'right', 0.2)),
    # 22 STARTING AT $9,800 over a slow-motion finished shower
    dict(src=P4 + 'IMG_7799.MOV', t0=beat(32), t1=beat(36), src_in=0.2, speed=0.45,
         zoom=[(0, 1.25), (0.15, 1.08), (1, 1.14)], grade='grey', dim=0.42, tin=('zoom', 'in', 0.27)),
    # 23 your dream shower
    dict(src=P1 + 'IMG_9054.MOV', t0=beat(36), t1=beat(38), src_in=0.25, speed=[(0, 1.6), (0.3, 0.75), (1, 0.75)],
         zoom=[(0, 1.12), (0.25, 1.02), (1, 1.07)], grade='beige', tin=('whip', 'left', 0.2)),
    # 24 ...is closer than you might think (pointing at camera)
    sync(P2 + 'IMG_9112.MOV', beat(38), beat(40), 21.72, 4.42, grade='talk',
         zoom=[(0, 1.10), (0.12, 1.0), (1, 1.04)], tin=('cut',)),
    # 25 Reach out to get started (both)
    sync(P2 + 'IMG_9116.MOV', beat(40), beat(43), 24.22, 0.12, grade='talk',
         zoom=[(0, 1.12), (0.1, 1.04), (1, 1.12)], tin=('whip', 'up', 0.2)),
    # 26 END: finished shower, slow push, CTA + logo
    dict(src=P1 + 'IMG_9040.MOV', t0=beat(43), t1=DUR, src_in=0.4, speed=0.62,
         zoom=[(0, 1.18), (0.08, 1.04), (1, 1.14)], grade='beige', dim_ramp=[(0, 0.0), (0.04, 0.18), (0.42, 0.25), (0.47, 0.52), (1, 0.6)],
         tin=('flash', 'orange', 0.5)),
]

# floating preview card in the hook
CARD = dict(src=P1 + 'IMG_9058.MOV', src_in=0.2, speed=0.9, t0=1.15, t1=3.55)
