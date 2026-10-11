"""Recorta personas/objetos (quita fondo) y genera versiones B/N de alto contraste."""
import sys
from PIL import Image, ImageOps, ImageEnhance
from rembg import remove, new_session

SRC, DST = "assets/fotos_src", "public/img"
sess = new_session("isnet-general-use")
for name in sys.argv[1:]:
    im = Image.open(f"{SRC}/{name}.jpg").convert("RGB")
    cut = remove(im, session=sess, alpha_matting=False)
    bbox = cut.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
    cut = cut.crop(bbox)
    cut.save(f"{DST}/{name}_recorte.png")
    # versión B/N con curva en S (estilo referencia)
    g = ImageOps.grayscale(cut.convert("RGB"))
    g = ImageEnhance.Contrast(g).enhance(1.25)
    bw = Image.merge("RGBA", (g, g, g, cut.getchannel("A")))
    bw.save(f"{DST}/{name}_bn.png")
    print(name, cut.size)
