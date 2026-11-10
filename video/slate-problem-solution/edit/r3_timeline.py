"""Reel 3 v2 — structure of 'Referencia_Reel_3_Slate': presenter on screen all the time; per problem an image card
at the top + mixed-type problem text mid-frame (word by word, synced to the off-camera voice); per solution a card at
the bottom with the treatment name; light leak into a closer shot for the closing with mixed-type captions.
Both original voices kept. No emojis."""
import os
from r3_engine import *
import ps_timeline as P                      # voice-derived times (SEG, C, word alignment), paths, grades

OFF, C, SEG, NSEG, TH = P.OFF, P.C, P.SEG, P.NSEG, P.TH
B, SAL, GRADE_T, GRADE_B, GRADE_Q, GRADE_A = P.B, P.SAL, P.GRADE_T, P.GRADE_B, P.GRADE_Q, P.GRADE_A
WB = P.WORDS_BY_SEG
VOICE_END = P.VOICE_END
END = round(VOICE_END + 0.60, 3)
CLOSE = C[16]                                # closing starts here (light leak)
s13d = P.s13d

def th(t0, t1, clip, z=1.0, cy=0.42):
    return dict(t0=t0, t1=t1, kind="t", clip=clip, z0=z, z1=z, cx=0.5, cy=cy, grade=GRADE_T)

SHOTS = [
 dict(t0=0.0, t1=C[0], kind="b", path=TH["IMG_7103"], src=0.10, z0=1.0, z1=1.0, cx=0.5, cy=0.42, grade=GRADE_T),  # hook
 th(C[0], C[10], "IMG_7103"),
 th(C[10], C[14], "IMG_7106"),
 th(C[14], CLOSE, "IMG_7108"),
 th(CLOSE, END, "IMG_7110", z=1.30, cy=0.42),                                                                      # closer shot
]

TOP = (int(0.36 * W), int(0.032 * H), 570, 316)
BOT = ((W - 680) // 2, int(0.712 * H), 680, 360)
TXT_Y = 0.645 * H            # between the shirt logo and the bottom card

def clip(path, src, box, cx=0.5, cy=0.5, wf=1.0, grade=GRADE_A):
    return CardClip(path, src, box[2], box[3], cx, cy, wf, grade)

def times_for(k, rows, lead=0.08):
    """Start time of each token = start of its first word in segment k."""
    ws = WB[k]; out = []; i = 0
    for row in rows:
        for tok in row:
            out.append(ws[min(i, len(ws) - 1)]["s"] - lead); i += len(tok[0].split())
    return out

PAIRS = [  # (q seg, top clip, problem rows, bottom cards [(clip, label, t_in or None, t_out or None)])
 (0, clip(B("st1_antes/IMG_4082.MOV"), 1.5, TOP, 0.5, 0.42, 0.78, GRADE_Q), [[("Pale or", "s")], [("dull skin", "S")]],
     [(clip(B("st3_proc/MVI_4552.MP4"), 1.0, BOT, 0.5, 0.38, 0.95), "Custom\nSpray Tan")]),
 (2, clip(B("st2_trans/IMG_1937.MOV"), 0.2, TOP, 0.5, 0.40, 0.72, GRADE_Q), [[("Need color", "s")], [("ASAP", "S")]],
     [(clip(B("st2_proc/IMG_1965.MOV"), 0.8, BOT, 0.5, 0.50, 0.95), "Rapid Tan")]),
 (4, clip(B("st1_antes/IMG_4083.MOV"), 0.8, TOP, 0.5, 0.42, 0.78, GRADE_Q), [[("Dry or", "s")], [("patchy skin", "S")]],
     [(clip(SAL("IMG_0802"), 0.2, BOT, 0.5, 0.55, 1.0), "Exfoliate\n24h Before")]),
 (6, clip(B("st1_desp/IMG_4123.mov"), 0.35, TOP, 0.5, 0.50, 0.95, GRADE_Q), [[("Tan fading", "s")], [("unevenly", "S")]],
     [(clip(SAL("IMG_0801"), 0.1, BOT, 0.5, 0.55, 1.0), "Moisturize\nDaily")]),
 (8, clip(B("st3_proc/MVI_4541.MP4"), 26.8, TOP, 0.42, 0.62, 0.95, GRADE_Q), [[("Tan sticking to", "s")], [("hands", "S"), ("and", "s"), ("feet", "S")]],
     [(clip(B("st2_cons/IMG_1949.MOV"), 20.5, BOT, 0.35, 0.42, 0.95), "Barrier Cream")]),
 (10, clip(B("st3_desp/IMG_2209.MOV"), 2.4, TOP, 0.5, 0.38, 0.85), [[("Going on", "s")], [("vacation", "S")]],
     [(clip(B("st2_lleg/IMG_1942.MOV"), 0.6, BOT, 0.5, 0.45, 1.0), "Book 1-2 Days\nBefore")]),
 (12, clip(B("st2_trans/IMG_1987.MOV"), 4.2, TOP, 0.5, 0.33, 0.85), [[("Wedding", "S"), ("or", "s")], [("special event", "S")]],
     [(clip(B("st2_lleg/IMG_1944.MOV"), 1.0, BOT, 0.5, 0.50, 1.0), "Proper Prep", None, s13d),
      (clip(B("st2_cons/IMG_1948.MOV"), 12.5, BOT, 0.45, 0.32, 0.95), "Custom Shade", s13d, None)]),
 (14, clip(B("st2_cons/IMG_1949.MOV"), 9.0, TOP, 0.35, 0.40, 0.90), [[("Not sure which", "s")], [("shade", "S"), ("or", "s"), ("solution", "S")], [("is right for you?", "s", "right")]],
     [(clip(B("st2_cons/IMG_1948.MOV"), 31.0, BOT, 0.5, 0.36, 1.0), "Personalized\nConsultation")]),
]

CLOSING = [  # (rows) — words of segments 16..19 in order
 [[("Every skin tone,", "s")]],
 [[("undertone,", "S")]],
 [[("and glow goal", "s")], [("is", "s"), ("different.", "S")]],
 [[("Your spray tan", "s")], [("should be", "s"), ("too.", "S")]],
 [[("If you relate", "s")], [("to any of this,", "s")]],
 [[("come see us at", "s")], [("Slate", "S")]],
 [[("and we'll find the", "s")], [("perfect tan", "S")], [("for you.", "s", "right")]],
]

def load_words(path=None, vmap=None):
    return []          # the reference shows no running captions in the problem/solution section

def build_overlays(words):
    ov = []
    # HOOK (client brief): first card + mixed type, then straight into problem 1
    ov.append(TopCard(clip(B("st1_proc/IMG_4096.mov"), 0.3, TOP, 0.42, 0.45, 0.85), 0.05, C[0] - 0.30, TOP[0:2] + TOP[2:]))
    ov.append(MixedText([[("Spray tan", "s")], [("problems?", "S")], [("we've got solutions!", "s", "right")]],
                        [0.10, 0.38, 0.78], C[0] - 0.22, cy=TXT_Y))
    for i, (q, topc, rows, bots) in enumerate(PAIRS):
        a = q + 1
        t_end = C[q + 2] if q + 2 < len(C) else CLOSE
        ov.append(TopCard(topc, C[q], t_end - 0.30, TOP))
        ov.append(MixedText(rows, times_for(q, rows), t_end - 0.22, cy=TXT_Y if len(rows) < 3 else TXT_Y - 0.012 * H))
        for j, bc in enumerate(bots):
            cl, label = bc[0], bc[1]
            t_in = bc[2] if len(bc) > 2 and bc[2] is not None else C[a]
            t_out = bc[3] if len(bc) > 3 and bc[3] is not None else t_end - 0.26
            last = (j == len(bots) - 1)
            ov.append(BottomCard(cl, t_in, t_out + (0.0 if last else 0.30), BOT, label, exit=last))
    # CLOSING: closer shot, mixed-type captions chunk by chunk
    cw = [w for k in range(16, NSEG) for w in WB[k]]
    starts = []; i = 0
    for rows in CLOSING:
        starts.append(i); i += sum(len(t[0].split()) for r in rows for t in r)
    for n, rows in enumerate(CLOSING):
        i0 = starts[n]; tt = []; i = i0
        for r in rows:
            for tok in r:
                tt.append(cw[i]["s"] - 0.08); i += len(tok[0].split())
        t_out = (cw[starts[n + 1]]["s"] - 0.16) if n + 1 < len(CLOSING) else END - 0.30
        ov.append(MixedText(rows, tt, t_out, cy=0.592 * H, d_out=0.12))
    return ov

POSTS = [LightLeak(CLOSE, 0.16, 0.32)]

SFX = [("thump", 0.05, -22.0)]
for q, *_ in PAIRS:
    t_end = C[q + 2] if q + 2 < len(C) else CLOSE
    SFX += [("thump", C[q] + 0.04, -22.0), ("whoosh", t_end - 0.36, -31.0), ("whoosh", C[q + 1] - 0.08, -33.0)]
SFX += [("riser", CLOSE - 0.72, -29.0), ("whoosh", CLOSE - 0.24, -24.0)]
