# Edit decision list. Durations are in beats (130 BPM). src = seconds in raw.mov.
# look: 'bw' (high-contrast black & white), 'lux' (teal/orange luxury grade), 'warm', 'neg'
# fx: set of per-clip effects
BPM = 130.0
BEAT = 60.0 / BPM
MUSIC_DROP = 14.786           # drop time inside the music file
DROP_BEAT = 16                # drop lands on this beat of the edit
MUSIC_START = MUSIC_DROP - DROP_BEAT * BEAT

C = lambda src, beats, look='lux', speed=1.0, fx=(), vert=False, zoom=(1.0, 1.08), text=None: dict(
    src=src, beats=beats, look=look, speed=speed, fx=set(fx), vert=vert, zoom=zoom, text=text)

EDL = [
    # --- A1: black & white flash montage (half-beat cuts) ---
    C(2109.0, 0.5, 'bw', fx=['punch']),            # marina yachts
    C(366.0, 0.5, 'bw', fx=['punch']),             # Cuatro Torres through Lambo windshield
    C(842.0, 0.5, 'bw', fx=['punch']),             # rooftop over Madrid
    C(1877.0, 0.5, 'bw', vert=True, fx=['punch']), # jet window above clouds
    C(354.0, 0.5, 'bw', fx=['punch']),             # Lambo steering wheel
    C(1461.0, 0.5, 'bw', fx=['punch']),            # skyscraper low angle
    C(924.0, 0.5, 'bw', fx=['punch']),             # dinner terrace night
    C(1882.0, 0.5, 'bw', vert=True, fx=['punch']), # walking to the jet on the tarmac
    C(390.5, 0.5, 'bw', fx=['punch']),             # sun flare, towers, red mirror
    C(2145.0, 0.5, 'bw', fx=['punch']),            # palms at the marina
    C(1800.5, 0.5, 'bw', fx=['punch']),            # jet cabin wide
    C(1761.0, 0.5, 'bw', fx=['punch', 'flashout']),  # friend waving in jet -> white flash
    # --- A2: vlog / talking in colour ---
    C(1760.0, 2, 'lux', fx=['flashin'], zoom=(1.12, 1.0)),  # selfie smiling in jet
    C(1804.0, 2, 'lux', zoom=(1.0, 1.05)),         # talking in the jet
    C(1839.0, 2, 'lux', zoom=(1.18, 1.22)),        # jump cut punch-in, hands out
    C(261.0, 2, 'lux', zoom=(1.0, 1.06)),           # talking in the Lambo
    C(400.2, 2, 'lux', fx=['negflick']),           # laughing in the Lambo -> negative build
    # --- B: DROP + title ---
    C(1460.0, 6, 'bw', speed=0.5, fx=['shake', 'title1', 'negpulse'], zoom=(1.05, 1.2)),
    # --- C: travel montage ---
    C(362.0, 2, 'lux', speed=1.5, fx=['punch', 'leak']),     # dash + towers
    C(303.5, 1, 'lux', fx=['punch']),                         # friend driving Lambo
    C(389.5, 1, 'lux', fx=['punch', 'rgb']),                  # towers + red mirror
    C(1891.5, 2, 'lux', fx=['punch']),                        # private terminal
    C(1880.5, 2, 'lux', speed=1.5, vert=True, fx=['punch']),  # walking to jet
    C(1888.0, 1, 'lux', vert=True, fx=['punch']),             # boarding
    C(1800.0, 1, 'lux', fx=['punch', 'rgb']),                 # cabin
    C(1872.0, 2, 'lux', speed=0.5, vert=True, fx=['punch', 'leak']),  # window above clouds
    C(1764.5, 1, 'lux', fx=['punch']),                        # friend in jet
    C(1877.5, 1, 'lux', vert=True, fx=['punch', 'rgb']),      # wing
    C(886.0, 2, 'lux', fx=['punch', 'flashout']),             # rooftop view
    # --- D: LET'S DO IT negative ---
    C(1839.5, 4, 'neg', fx=['letsdoit', 'shake'], zoom=(1.0, 1.1)),
    # --- E: sunset / night ---
    C(842.5, 2, 'warm', fx=['flashin', 'leak']),              # rooftop sunset
    C(864.5, 1, 'warm', fx=['punch']),                         # laptop on marble table, view
    C(919.5, 2, 'warm', fx=['punch', 'leak']),                 # dinner, toasting
    C(959.0, 1, 'warm', fx=['punch', 'rgb']),                  # wine glasses
    C(1289.0, 1, 'warm', fx=['punch']),                        # garden lights night
    C(2108.0, 2, 'warm', fx=['punch', 'leak']),                # marina yachts sunset
    C(2145.5, 1, 'warm', fx=['punch']),                        # palms
    C(2231.0, 2, 'warm', fx=['punch', 'rgb']),                 # shopping bags
    C(2105.0, 2, 'warm', fx=['punch', 'flashout']),            # him at the marina
    # --- F: final title ---
    C(886.5, 7, 'warm', speed=0.6, fx=['flashin', 'title2', 'fadeout'], zoom=(1.25, 1.05)),
]

TOTAL_BEATS = sum(c['beats'] for c in EDL)
