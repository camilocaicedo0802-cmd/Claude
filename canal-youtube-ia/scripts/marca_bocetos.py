"""Genera la muestra de paleta y los bocetos (wireframes) de las 3 miniaturas conceptuales.
Son esquemas de composición, no ilustraciones finales. Fuente provisional: DejaVu (la final es Anton).
Uso: python3 marca_bocetos.py marca/
"""
import sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]
PAL = [("Noche de archivo", "#14161F"), ("Tinta", "#1E1A16"), ("Papel amate", "#EADBC0"), ("Hueso", "#F6F0E4"),
       ("Cochinilla", "#B3272D"), ("Azul maya", "#3D8DB5"), ("Oro muisca", "#D9A637"), ("Verde selva", "#2E5B45")]
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f = lambda p, s: ImageFont.truetype(p, s)
# Paleta
im = Image.new("RGB", (1600, 420), "#FFFFFF"); d = ImageDraw.Draw(im)
for i, (n, h) in enumerate(PAL):
    x = 20 + i * 197; d.rectangle([x, 20, x + 180, 300], fill=h, outline="#999999")
    d.text((x, 315), n, fill="#111", font=f(B, 17)); d.text((x, 345), h, fill="#444", font=f(R, 20))
d.text((20, 385), "Paleta: pigmentos históricos americanos (cochinilla, azul maya, oro muisca, papel amate)", fill="#333", font=f(R, 18))
im.save(f"{OUT}/paleta.png")

def thumb(fname, bg, words, accent_idx, scene, stamp, note):
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    # luz de una sola fuente
    for r in range(380, 0, -20):
        c = 30 + (380 - r) // 8
        d.ellipse([W * 0.62 - r, H * 0.35 - r, W * 0.62 + r, H * 0.35 + r], fill=(c, c, c + 10))
    # protagonista (silueta de marcador)
    d.rounded_rectangle([700, 150, 1120, 720], 60, fill="#2A2D3A", outline="#EADBC0", width=4)
    d.text((760, 420), scene, fill="#EADBC0", font=f(R, 26))
    # evidencia / documento
    d.rectangle([60, 470, 330, 680], fill="#EADBC0"); d.text((80, 560), "evidencia:\nmapa / crónica", fill="#1E1A16", font=f(R, 24))
    # texto 2-3 palabras
    y = 70
    for i, w in enumerate(words):
        col = "#B3272D" if i == accent_idx else "#F6F0E4"
        fs = 110
        for dx in (-5, 5):
            for dy in (-5, 5): d.text((60 + dx, y + dy), w, fill="#1E1A16", font=f(B, fs))
        d.text((60, y), w, fill=col, font=f(B, fs)); y += 125
    # sello de serie
    d.ellipse([1110, 30, 1250, 170], outline="#B3272D", width=8); d.text((1180, 100), stamp, fill="#B3272D", font=f(B, 18), anchor="mm")
    d.text((20, 690), note, fill="#999", font=f(R, 18))
    im.save(f"{OUT}/{fname}")
thumb("miniatura_concepto_1_llorona.png", "#14161F", ["¿EXISTIÓ?"], 0, "mujer de espaldas\nrebozo blanco\njunto al río\n(reflejo en el agua)", "LEYENDA?", "Concepto 1 · La verdadera historia de La Llorona · boceto de composición")
thumb("miniatura_concepto_2_colombia.png", "#1E1A16", ["¿POR QUÉ", "ÉL?"], 1, "navegante de época\nmirando un mapa\nrotulado COLOMBIA", "HISTORIA", "Concepto 2 · ¿Por qué Colombia se llama Colombia? · boceto de composición")
thumb("miniatura_concepto_3_tenochtitlan.png", "#2E5B45", ["VIVÍAS", "AQUÍ"], 1, "joven mexica en canoa\nmira a cámara\nciudad al amanecer", "1518", "Concepto 3 · Así vivías si nacías en Tenochtitlan · boceto de composición")
print("ok")
