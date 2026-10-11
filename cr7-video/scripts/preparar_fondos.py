# Recorta a 1080x1920 (cover) y aplica la gradación base del modo oscuro (estilo.md §2):
# cálida, desaturada, negros levantados, exposición baja. Viñeta/grano/empuje se hacen en Remotion.
import sys, numpy as np
from PIL import Image, ImageFilter
def prep(src, dst, fx=0.5, fy=0.5, dark=True):
    im = Image.open(src).convert("RGB")
    W, H = 1080, 1920
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int((im.width - W) * fx); y = int((im.height - H) * fy)
    im = im.crop((x, y, x + W, y + H))
    if s > 1.6: im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    a = np.asarray(im).astype(np.float32) / 255.0
    if dark:
        lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[..., None]
        a = lum + (a - lum) * 0.55                              # saturación 55 %
        a = a * np.array([1.06, 1.0, 0.88])                      # tinte cálido
        a = np.clip(a, 0, 1) ** 1.25 * 0.78 + 0.035              # oscurecer + levantar negros
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(dst, quality=92)
    print("ok", dst)
if __name__ == "__main__":
    D = "/tmp/claude-0/-home-user-Claude/0f0c8e44-325e-5f2d-b499-3efb52d8085e/scratchpad/dl/"
    O = "public/img/oscuro/"
    jobs = [("ov_madeira_cliffs_0", "intro_1_acantilado", .5), ("ov_madeira_sunset_15", "intro_2_olas", .62),
            ("ov_funchal_8", "intro_3_calle", .5), ("ov_madeira_sunset_19", "intro_4_roca", .5),
            ("ov_madeira_sunset_9", "intro_5_costa", .55), ("ov_madeira_cliffs_3", "intro_6_acantilado2", .5),
            ("ov_kidball_9", "nino_silueta", .5), ("ov_kidball_8", "ninos_jugando", .47),
            ("ov_kidball_13", "balon_escalera", .18), ("ov_kidball_19", "noche_entreno", .55),
            ("ov_juve_2", "bernabeu", .5)]
    for src, name, fx in jobs: prep(D + src + ".jpg", O + name + ".jpg", fx)
