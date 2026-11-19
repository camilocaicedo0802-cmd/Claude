import sys, os
sys.path.insert(0, "/home/user/cr/edit")
import cv2, maps as M
from engine import YELLOW, RED, WHITE
out = "/tmp/claude-0/-home-user-Claude/f7fb94cd-aa23-591c-9ce9-57a58b6bd5c4/scratchpad/maps"
os.makedirs(out, exist_ok=True)
GOLD = YELLOW
tests = {
 "us": ("cr_us", [(0, -121.0, 44.5, 2.2), (3, -121.0, 44.5, 2.3)], [dict(type="pin", at="cr_portland", t0=0, label="PORTLAND", side="l", box=True, size=36)]),
 "reg": ("cr_reg", [(0, -121.75, 45.6, 0.62), (3, -121.75, 45.6, 0.65)], [dict(type="route", ll=M.cr_ll("line"), t0=0, draw=1.0, color=GOLD, width=6),
        dict(type="pin", at="cr_portland", t0=0, label="PORTLAND", side="l", box=True, size=34), dict(type="pin", at="cr_dalles", t0=0, label="THE DALLES", side="r", box=True, size=34),
        dict(type="pin", at="cr_mthood", t0=0, label="MOUNT HOOD", side="r", box=True, size=30), dict(type="pin", at="cr_maryhill", t0=0, label="MARYHILL", side="r", box=True, size=30)]),
 "gorge": ("cr_gorge", [(0, -121.75, 45.62, 0.5), (3, -121.75, 45.62, 0.52)], [dict(type="route", ll=M.cr_ll("line"), t0=0, draw=1.0, color=GOLD, width=6),
        dict(type="pin", at="cr_multnomah", t0=0, label="MULTNOMAH FALLS", side="l", box=True, size=30), dict(type="pin", at="cr_mitchell", t0=0, label="MITCHELL POINT", side="l", box=True, size=30),
        dict(type="pin", at="cr_twin", t0=0, label="TÚNELES GEMELOS", side="r", box=True, size=30)]),
 "west": ("cr_west", [(0, -122.17, 45.56, 0.45), (3, -122.17, 45.56, 0.47)], [dict(type="route", ll=M.cr_ll("west"), t0=0, draw=1.0, color=GOLD, width=7),
        dict(type="pin", at="cr_crown", t0=0, label="VISTA HOUSE", side="l", box=True, size=30), dict(type="pin", at="cr_multnomah", t0=0, label="MULTNOMAH FALLS", side="r", box=True, size=30)]),
 "east": ("cr_east", [(0, -121.47, 45.69, 0.45), (3, -121.47, 45.69, 0.47)], [dict(type="route", ll=M.cr_ll("line"), t0=0, draw=1.0, color=GOLD, width=7),
        dict(type="pin", at="cr_mitchell", t0=0, label="MITCHELL POINT", side="l", box=True, size=30), dict(type="pin", at="cr_twin", t0=0, label="TÚNELES GEMELOS", side="r", box=True, size=30),
        dict(type="pin", at="cr_mosier", t0=0, label="MOSIER", side="r", box=True, size=30), dict(type="pin", at="cr_hoodriver", t0=0, label="HOOD RIVER", side="r", box=True, size=30)]),
 "ch": ("cr_ch", [(0, 8.2, 46.9, 0.8), (3, 8.2, 46.9, 0.82)], [dict(type="pin", at="cr_lucerne", t0=0, label="LUCERNA", side="l", box=True, size=34),
        dict(type="pin", at="cr_flueelen", t0=0, label="AXENSTRASSE", side="r", box=True, size=34)]),
}
for k in (sys.argv[1:] or tests):
    name, cams, layers = tests[k]
    sc = M.MapScene(name, cams, layers)
    im = sc.frame(2.5)
    cv2.imwrite(f"{out}/{k}.jpg", cv2.cvtColor(im, cv2.COLOR_RGB2BGR) if im.shape[2] == 3 else im, [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(k, im.shape)
