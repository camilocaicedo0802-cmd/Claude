import sys, os
sys.path.insert(0, "/home/user/cr/edit")
import cv2, gfx16 as G
out = "/tmp/claude-0/-home-user-Claude/f7fb94cd-aa23-591c-9ce9-57a58b6bd5c4/scratchpad/gfx"
os.makedirs(out, exist_ok=True)
T = [("hang", lambda: G.hang(3.0, 5, road_t=1.5)), ("hang2", lambda: G.hang(4.0, 5, road_t=0.1, i84_t=1.0, cut_t=2.5)),
     ("win", lambda: G.windows(3.6, 6, car_t=1.0)), ("rule", lambda: G.rule5(3.5, 5)), ("flag", lambda: G.flagmen(3.5, 5)),
     ("sq", lambda: G.squeeze(3.0, 4, truck_t=2.0)), ("fill", lambda: G.fill(4.0, 6)), ("dig", lambda: G.fill(4.0, 6, mode="dig", reveal_t=3.5)),
     ("reb", lambda: G.fill(3.0, 5, mode="rebuilt")), ("carv", lambda: G.carving(4.0, 5)), ("days", lambda: G.days(5.0, 6)),
     ("fun", lambda: G.funnel(3.0, 5)), ("shel", lambda: G.shelter(2.8, 5)), ("era", lambda: G.era(5.0, 6)), ("pri", lambda: G.prices(3.0, 4))]
for n, f in T:
    if len(sys.argv) > 1 and n not in sys.argv[1:]: continue
    im = f()
    cv2.imwrite(f"{out}/{n}.jpg", cv2.cvtColor(cv2.resize(im, (640, 360)), cv2.COLOR_RGB2BGR))
