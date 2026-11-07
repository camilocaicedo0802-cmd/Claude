import sys, glob
from PIL import Image, ImageDraw
fs=sorted(glob.glob(sys.argv[1]+'/s_*.png')); out=sys.argv[2]; cols=int(sys.argv[3]) if len(sys.argv)>3 else 6
w,h=270,480
rows=(len(fs)+cols-1)//cols
c=Image.new('RGB',(cols*w,rows*(h+18)),'white'); d=ImageDraw.Draw(c)
for i,f in enumerate(fs):
    im=Image.open(f).resize((w,h),Image.LANCZOS); x=(i%cols)*w; y=(i//cols)*(h+18)
    c.paste(im,(x,y+18)); d.text((x+4,y+3),f.split('s_')[-1][:-4],fill='black')
c.save(out)
