"""Edit decision list for reel LB-OCT-12 ("Rutina después del trabajo").

Times are in seconds of each raw Drive clip. The cuerpo numbers follow the script table.
"""

FPS = 30
W, H = 1080, 1920

# Raw clips, as they are named in the --raw folder -> file in the client's Drive folder.
CLIPS = {
    "c1": "1. Rutina después del trabajo",
    "c2": "2. Rutina después del trabajo",
    "c345": "3,4, 5. Rutina después del trabajo",
    "c6": "6. Rutina después del trabajo",
    "c78": "7,8. Rutina después del trabajo",
}

# grade: per-shot color preset (see video.py GRADES)
# ramp: (src_t_start, src_t_end, final_speed) eases playback speed down for a slow-motion pass
# zoom: (z0, z1, cx, cy) punch-in that pushes from z0 to z1 around (cx, cy) in source-relative coords
# mask_from: source time where the person-mask reveal of the next shot starts
SHOTS = [
    # Cuerpo 1: llega a casa; al pasar frente a la cámara, la cocina aparece detrás de ella (máscara)
    dict(id="1a", cuerpo=1, src="c1", tin=1.95, tout=4.60, grade="entry"),
    dict(id="1b", cuerpo=1, src="c1", tin=7.25, tout=11.15, grade="entry",
         ramp=(10.25, 10.55, 0.55), mask_from=10.60),
    # Cuerpo 2: se sirve la bebida; pasa por el frente de la cámara y conecta con el pasillo
    dict(id="2a", cuerpo=2, src="c2", tin=0.20, tout=5.95, grade="kitchen"),
    dict(id="2b", cuerpo=2, src="c2", tin=8.30, tout=9.70, grade="kitchen", mask_from=9.40),
    # Cuerpo 3: entra al pasillo, toma frontal -> corte
    dict(id="3", cuerpo=3, src="c345", tin=2.55, tout=6.95, grade="hall"),
    # Cuerpo 4: entra a la habitación, toma posterior -> corte
    dict(id="4a", cuerpo=4, src="c345", tin=10.55, tout=12.10, grade="room"),
    dict(id="4b", cuerpo=4, src="c345", tin=13.95, tout=17.85, grade="room"),
    # Cuerpo 5: entra a la habitación (frontal) y al baño; cubre la cámara con el cabello
    dict(id="5a", cuerpo=5, src="c345", tin=118.62, tout=120.95, grade="dark"),
    dict(id="5b", cuerpo=5, src="c345", tin=122.70, tout=126.40, grade="dark"),
    # Cuerpo 6: descubre la cámara al bajar la bata; la cubre al quitarse la camisa
    dict(id="6a", cuerpo=6, src="c6", tin=1.45, tout=4.65, grade="closet"),
    dict(id="6b", cuerpo=6, src="c6", tin=7.00, tout=10.50, grade="closet"),
    # Cuerpo 7: descubre la cámara al ponerse la bata; la cubre con el cabello
    dict(id="7a", cuerpo=7, src="c78", tin=0.55, tout=4.70, grade="bath"),
    dict(id="7b", cuerpo=7, src="c78", tin=8.40, tout=10.25, grade="bath"),
    dict(id="7c", cuerpo=7, src="c78", tin=12.40, tout=16.40, grade="bath"),
    # Cuerpo 8: abre desde la pierna; microtomas del reto en el teléfono y del calendario; masaje
    dict(id="8a", cuerpo=8, src="c78", tin=72.45, tout=74.40, grade="bath"),
    dict(id="8b", cuerpo=8, src="c78", tin=24.00, tout=25.95, grade="bath"),
    dict(id="8c", cuerpo=8, src="c78", tin=61.70, tout=63.85, grade="bath", zoom=(1.40, 1.50, 0.60, 0.47)),
    dict(id="8d", cuerpo=8, src="c78", tin=75.30, tout=77.05, grade="bath", zoom=(1.80, 1.92, 0.80, 0.73)),
    dict(id="8e", cuerpo=8, src="c78", tin=89.25, tout=95.40, grade="bath"),
]

# Transition from SHOTS[i] to SHOTS[i + 1]: (kind, frames). "mask" lengths come from mask_from.
# dissolve: soft cross-dissolve inside a cuerpo
# mask: the next scene enters behind her as she passes the camera (person segmentation)
# cover: camera covered by hair / robe / shirt on both sides, blended while covered
TRANSITIONS = [
    ("dissolve", 6),   # 1a -> 1b
    ("mask", None),    # 1b -> 2a  (efecto máscara)
    ("dissolve", 6),   # 2a -> 2b
    ("mask", None),    # 2b -> 3   (pasa frente a la cámara: corte que conecta)
    ("cut", 0),        # 3 -> 4    (salida: corte)
    ("dissolve", 6),   # 4a -> 4b
    ("cut", 0),        # 4b -> 5a  (salida: corte)
    ("dissolve", 6),   # 5a -> 5b
    ("cover", 8),      # 5b -> 6a  (cabello cubre / bata descubre)
    ("dissolve", 6),   # 6a -> 6b
    ("cover", 8),      # 6b -> 7a  (camisa cubre / bata descubre)
    ("dissolve", 7),  # 7a -> 7b
    ("dissolve", 7),  # 7b -> 7c
    ("cover", 8),      # 7c -> 8a  (cabello cubre / abre desde la pierna)
    ("dissolve", 6),   # 8a -> 8b
    ("dissolve", 6),   # 8b -> 8c
    ("dissolve", 6),   # 8c -> 8d
    ("dissolve", 6),   # 8d -> 8e
]
END_FADE = 14  # frames of fade at the very end

TEXT1 = "No todo tiene que ser productividad."
TEXT2 = "A veces hay que parar, respirar y dedicarte un momento."


def shot_times(shot):
    """Source time of every output frame of a shot, honoring an optional speed ramp."""
    times, t = [], shot["tin"]
    ramp = shot.get("ramp")
    while t < shot["tout"] - 1e-6:
        times.append(t)
        speed = 1.0
        if ramp:
            a, b, s = ramp
            if t >= b:
                speed = s
            elif t > a:
                speed = 1.0 + (s - 1.0) * (t - a) / (b - a)
        t += speed / FPS
    return times


def build_timeline():
    """Place shots on the output timeline. Returns (shots with 'start'/'times', total frames)."""
    placed, cursor = [], 0
    for i, shot in enumerate(SHOTS):
        s = dict(shot)
        s["times"] = shot_times(shot)
        if i > 0:
            kind, frames = TRANSITIONS[i - 1]
            prev = placed[-1]
            if kind == "mask":
                frames = sum(1 for t in prev["times"] if t >= prev["mask_from"])
            prev["out_kind"], prev["out_frames"] = kind, frames
            s["in_kind"], s["in_frames"] = kind, frames
            cursor -= frames
        s["start"] = cursor
        cursor += len(s["times"])
        placed.append(s)
    return placed, cursor


if __name__ == "__main__":
    shots, total = build_timeline()
    for s in shots:
        print(f'{s["id"]:>3} cuerpo {s["cuerpo"]}  out {s["start"] / FPS:6.2f}-{(s["start"] + len(s["times"])) / FPS:6.2f}s'
              f'  src {s["src"]} {s["tin"]:.2f}-{s["tout"]:.2f}  in={s.get("in_kind", "-")}:{s.get("in_frames", 0)}')
    print(f"total {total} frames = {total / FPS:.2f}s")
