# Edit decision list. Durations are in edit units: half a beat of the song
# (Myke Towers - "Pauta y Flow", 80.5 BPM -> 1 beat = 0.7454 s, 1 unit = 0.3727 s).
# src = seconds in raw.mov, or (clip_name, seconds) for the extra iPhone clips.
# look: 'bw' (high-contrast black & white), 'lux' (teal/orange luxury grade), 'warm', 'neg'
SONG_BEAT = 0.7454
BEAT = SONG_BEAT / 2          # edit unit
MUSIC_FILE = 'music2/pauta.mp3'
MUSIC_DROP = 71.712           # bass comes back in (chorus) inside the song
DROP_BEAT = 20                # ...and lands on this unit of the edit, with the title
MUSIC_START = MUSIC_DROP - DROP_BEAT * BEAT

# vert: vertical source -> crop to fill 16:9; value = crop centre (0..1 of the picture height),
#       a number or a (start, end) pair to pan during the clip. iPhone clips are always vertical.
# anchor: (x, y) fractions the zoom is centred on (y < 0.5 keeps heads in frame)
C = lambda src, beats, look='lux', speed=1.0, fx=(), vert=None, zoom=(1.0, 1.08), anchor=(0.5, 0.5): dict(
    src=src, beats=beats, look=look, speed=speed, fx=set(fx), vert=vert, zoom=zoom, anchor=anchor)

TOP = (0.5, 0.18)
J8829, J8965, J8967, J9018 = 'IMG_8829', 'IMG_8965', 'IMG_8967', 'IMG_9018'

EDL = [
    # --- A1: black & white flash montage (16th-note cuts) ---
    C(2109.0, 0.5, 'bw', fx=['punch']),                         # marina yachts
    C(366.0, 0.5, 'bw', fx=['punch']),                          # Cuatro Torres through Lambo windshield
    C((J8829, 0.6), 0.5, 'bw', vert=0.45, fx=['punch']),        # walking up to the private jet
    C(1877.0, 0.5, 'bw', vert=0.5, fx=['punch']),               # jet window above clouds
    C(354.0, 0.5, 'bw', fx=['punch']),                          # Lambo steering wheel
    C(1461.0, 0.5, 'bw', fx=['punch']),                         # skyscraper low angle
    C((J8967, 0.3), 0.5, 'bw', vert=0.66, fx=['punch']),         # feet up in first class
    C(1883.0, 0.5, 'bw', vert=0.46, fx=['punch']),              # walking away from the jet
    C(390.5, 0.5, 'bw', fx=['punch']),                          # sun flare, towers, red mirror
    C(1800.5, 0.5, 'bw', fx=['punch'], anchor=TOP),             # him in the jet cabin
    C((J8829, 16.2), 0.5, 'bw', vert=0.44, fx=['punch']),        # walking along the jet
    C(283.0, 0.5, 'bw', fx=['punch', 'flashout'], anchor=TOP),  # him smiling in the Lambo -> white flash
    # --- A2: vlog / talking in colour ---
    C((J8967, 8.3), 3, 'lux', vert=0.6, fx=['flashin'], zoom=(1.08, 1.0)),  # selfie in first class
    C(1804.0, 3, 'lux', zoom=(1.0, 1.05), anchor=TOP),          # talking in the private jet
    C(1839.0, 2, 'lux', zoom=(1.16, 1.2), anchor=TOP),          # jump cut punch-in, hands out
    C(261.0, 3, 'lux', zoom=(1.0, 1.06), anchor=TOP),           # talking in the Lambo
    C(400.2, 3, 'lux', fx=['negflick'], anchor=TOP),            # laughing in the Lambo -> negative build
    # --- B: DROP (bass + chorus) + title ---
    C(1460.0, 8, 'bw', speed=0.5, fx=['shake', 'title1', 'negpulse'], zoom=(1.05, 1.2)),
    # --- C: Lambo + private jet ---
    C(362.0, 2, 'lux', speed=1.5, fx=['punch', 'leak']),        # Lambo dash + towers
    C(439.0, 1, 'lux', fx=['punch'], anchor=TOP),               # him laughing in the sun, Lambo
    C(389.5, 1, 'lux', fx=['punch', 'rgb']),                    # towers + red mirror
    C(477.0, 1, 'lux', fx=['punch'], anchor=TOP),               # him talking in the Lambo
    C(1891.5, 1, 'lux', fx=['punch'], anchor=TOP),              # private terminal
    C((J8829, 0.0), 2, 'lux', vert=(0.48, 0.44), fx=['punch']),        # walking to the jet's stairs
    C((J8829, 12.4), 2, 'lux', vert=0.37, fx=['punch', 'rgb']),  # stepping off the jet
    C((J8829, 15.6), 2, 'lux', vert=(0.48, 0.5), fx=['punch']),        # walking along the jet
    C(1881.5, 2, 'lux', speed=1.25, vert=(0.47, 0.44), fx=['punch']),  # walking from the jet
    C(1888.5, 1, 'lux', vert=0.42, fx=['punch']),               # getting into the car
    C(1866.0, 1, 'lux', fx=['punch', 'rgb'], anchor=TOP),       # him close by the jet window
    C(1872.0, 2, 'lux', speed=0.5, vert=(0.46, 0.54), fx=['punch', 'leak']),  # window above clouds
    C(1795.0, 1, 'lux', fx=['punch'], anchor=TOP),              # him seated in the jet
    C(886.0, 1, 'lux', fx=['punch', 'flashout']),               # rooftop view
    # --- D: LET'S DO IT negative ---
    C(1839.5, 5, 'neg', fx=['letsdoit', 'shake'], zoom=(1.0, 1.1), anchor=TOP),
    # --- E: first class, sunset, night ---
    C(842.5, 2, 'warm', fx=['flashin', 'leak']),                # rooftop sunset
    C((J8967, 5.2), 1, 'warm', vert=0.55, fx=['punch']),        # first-class suite window
    C((J9018, 9.0), 2, 'warm', vert=0.62, fx=['punch']),        # dinner on board, talking
    C(918.1, 1, 'warm', fx=['punch'], anchor=TOP),              # him at dinner with a glass
    C(939.5, 2, 'warm', fx=['punch', 'leak'], anchor=TOP),      # him with the wine, laughing
    C(1289.0, 1, 'warm', fx=['punch', 'rgb'], anchor=TOP),      # garden lights night
    C(2108.0, 2, 'warm', fx=['punch', 'leak']),                 # marina yachts sunset
    C(2145.5, 1, 'warm', fx=['punch']),                         # palms
    C(2231.0, 2, 'warm', fx=['punch', 'rgb']),                  # shopping bags
    C(2105.0, 2, 'warm', fx=['punch', 'flashout'], anchor=TOP), # him at the marina
    # --- F: final title ---
    C(886.5, 9, 'warm', speed=0.6, fx=['flashin', 'title2', 'fadeout'], zoom=(1.25, 1.05)),
]

TOTAL_BEATS = sum(c['beats'] for c in EDL)
