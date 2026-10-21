# Edit decision list. Durations are in beats (130 BPM). src = seconds in raw.mov.
# look: 'bw' (high-contrast black & white), 'lux' (teal/orange luxury grade), 'warm', 'neg'
# fx: set of per-clip effects
BPM = 130.0
BEAT = 60.0 / BPM
MUSIC_DROP = 14.786           # drop time inside the music file
DROP_BEAT = 16                # drop lands on this beat of the edit
MUSIC_START = MUSIC_DROP - DROP_BEAT * BEAT

# vert: vertical (pillarboxed) source -> crop to fill 16:9; value = crop centre (0..1 of height),
#       either a number or a (start, end) pair to pan during the clip
# anchor: (x, y) fractions the zoom is centred on (y < 0.5 keeps heads in frame)
C = lambda src, beats, look='lux', speed=1.0, fx=(), vert=None, zoom=(1.0, 1.08), anchor=(0.5, 0.5): dict(
    src=src, beats=beats, look=look, speed=speed, fx=set(fx), vert=vert, zoom=zoom, anchor=anchor)

TOP = (0.5, 0.18)

EDL = [
    # --- A1: black & white flash montage (half-beat cuts) ---
    C(2109.0, 0.5, 'bw', fx=['punch']),                  # marina yachts
    C(366.0, 0.5, 'bw', fx=['punch']),                   # Cuatro Torres through Lambo windshield
    C(842.0, 0.5, 'bw', fx=['punch']),                   # rooftop over Madrid
    C(1877.0, 0.5, 'bw', vert=0.5, fx=['punch']),        # jet window above clouds
    C(354.0, 0.5, 'bw', fx=['punch']),                   # Lambo steering wheel
    C(1461.0, 0.5, 'bw', fx=['punch']),                  # skyscraper low angle
    C(924.0, 0.5, 'bw', fx=['punch'], anchor=TOP),       # him at the dinner table
    C(1883.0, 0.5, 'bw', vert=0.46, fx=['punch']),       # walking away from the jet
    C(390.5, 0.5, 'bw', fx=['punch']),                   # sun flare, towers, red mirror
    C(2145.0, 0.5, 'bw', fx=['punch']),                  # palms at the marina
    C(1800.5, 0.5, 'bw', fx=['punch'], anchor=TOP),      # him in the jet cabin
    C(283.0, 0.5, 'bw', fx=['punch', 'flashout'], anchor=TOP),  # him smiling in the Lambo -> white flash
    # --- A2: vlog / talking in colour ---
    C(1760.0, 2, 'lux', fx=['flashin'], zoom=(1.12, 1.0), anchor=TOP),  # selfie smiling in jet
    C(1804.0, 2, 'lux', zoom=(1.0, 1.05), anchor=TOP),   # talking in the jet
    C(1839.0, 2, 'lux', zoom=(1.16, 1.2), anchor=TOP),   # jump cut punch-in, hands out
    C(261.0, 2, 'lux', zoom=(1.0, 1.06), anchor=TOP),    # talking in the Lambo
    C(400.2, 2, 'lux', fx=['negflick'], anchor=TOP),     # laughing in the Lambo -> negative build
    # --- B: DROP + title ---
    C(1460.0, 6, 'bw', speed=0.5, fx=['shake', 'title1', 'negpulse'], zoom=(1.05, 1.2)),
    # --- C: travel montage ---
    C(362.0, 2, 'lux', speed=1.5, fx=['punch', 'leak']),             # dash + towers
    C(439.0, 1, 'lux', fx=['punch'], anchor=TOP),                     # him laughing in the sun, Lambo
    C(389.5, 1, 'lux', fx=['punch', 'rgb']),                          # towers + red mirror
    C(477.0, 1, 'lux', fx=['punch'], anchor=TOP),                     # him talking in the Lambo
    C(1891.5, 1, 'lux', fx=['punch'], anchor=TOP),                    # private terminal
    C(1881.5, 2, 'lux', speed=1.25, vert=(0.47, 0.44), fx=['punch']), # getting off: walking from the jet
    C(1886.0, 1, 'lux', vert=(0.42, 0.38), fx=['punch', 'rgb']),      # closer, jet behind him
    C(1888.5, 1, 'lux', vert=0.42, fx=['punch']),                     # getting into the car
    C(1800.0, 1, 'lux', fx=['punch'], anchor=TOP),                    # him in the cabin
    C(1866.0, 1, 'lux', fx=['punch', 'rgb'], anchor=TOP),             # him close by the jet window
    C(1872.0, 2, 'lux', speed=0.5, vert=(0.46, 0.54), fx=['punch', 'leak']),  # window above clouds
    C(1795.0, 1, 'lux', fx=['punch'], anchor=TOP),                    # him seated in the jet
    C(886.0, 1, 'lux', fx=['punch', 'flashout']),                     # rooftop view
    # --- D: LET'S DO IT negative ---
    C(1839.5, 4, 'neg', fx=['letsdoit', 'shake'], zoom=(1.0, 1.1), anchor=TOP),
    # --- E: sunset / night ---
    C(842.5, 2, 'warm', fx=['flashin', 'leak']),                      # rooftop sunset
    C(864.5, 1, 'warm', fx=['punch']),                                # laptop on marble table, view
    C(918.1, 1, 'warm', fx=['punch'], anchor=TOP),                    # him at dinner with a glass
    C(939.5, 2, 'warm', fx=['punch', 'leak'], anchor=TOP),            # him with the wine, laughing
    C(1289.0, 1, 'warm', fx=['punch', 'rgb'], anchor=TOP),            # garden lights night
    C(2108.0, 2, 'warm', fx=['punch', 'leak']),                       # marina yachts sunset
    C(2145.5, 1, 'warm', fx=['punch']),                               # palms
    C(2231.0, 2, 'warm', fx=['punch', 'rgb']),                        # shopping bags
    C(2105.0, 2, 'warm', fx=['punch', 'flashout'], anchor=TOP),       # him at the marina
    # --- F: final title ---
    C(886.5, 7, 'warm', speed=0.6, fx=['flashin', 'title2', 'fadeout'], zoom=(1.25, 1.05)),
]

TOTAL_BEATS = sum(c['beats'] for c in EDL)
