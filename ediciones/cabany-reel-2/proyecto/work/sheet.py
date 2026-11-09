import sys, glob
from PIL import Image, ImageDraw, ImageFont
files = sys.argv[2:]
W, H = 360, 640
cols = min(5, len(files)); rows = (len(files) + cols - 1) // cols
sh = Image.new('RGB', (W * cols, H * rows), 'black')
f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 18)
for k, p in enumerate(files):
    im = Image.open(p).resize((W, H))
    ImageDraw.Draw(im).text((6, 6), p.split('/')[-1], fill=(255, 0, 255), font=f)
    sh.paste(im, ((k % cols) * W, (k // cols) * H))
sh.save(sys.argv[1])
