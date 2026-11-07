import sys
from PIL import Image, ImageDraw, ImageFont
F=sys.argv[1]
def font(name, size, wght=None, extra=None):
    f=ImageFont.truetype(F+'/'+name, size)
    try:
        axes=f.get_variation_axes()
        vals=[]
        for a in axes:
            n=a['name'] if isinstance(a['name'],str) else a['name'].decode()
            if n.lower().startswith('weight') and wght: vals.append(wght)
            elif extra and n.lower() in extra: vals.append(extra[n.lower()])
            else: vals.append(a['default'])
        f.set_variation_by_axes(vals)
    except Exception: pass
    return f
def sheet(ref, refbox, text, cands, out, size):
    r=Image.open(ref).crop(refbox)
    rows=[r]
    for name,w in cands:
        f=font(name,size,w)
        im=Image.new('RGB',(r.width,int(size*1.5)),(90,80,70)); d=ImageDraw.Draw(im)
        d.text((10,5),text,font=f,fill='white')
        ImageDraw.Draw(im).text((r.width-200,2),f'{name[:22]} {w or ""}',fill='yellow')
        rows.append(im)
    H=sum(x.height for x in rows); c=Image.new('RGB',(r.width,H)); y=0
    for x in rows: c.paste(x,(0,y)); y+=x.height
    c.save(out)
R=sys.argv[2]
sheet(R+'/t_14.6.png',(150,330,560,450),'techniques,',[('PlayfairDisplay-Italic[wght].ttf',500),('PlayfairDisplay-Italic[wght].ttf',600),('CormorantGaramond-Italic[wght].ttf',700),('Lora-Italic[wght].ttf',500),('DMSerifDisplay-Italic.ttf',None),('BodoniModa-Italic[opsz,wght].ttf',500),('InstrumentSerif-Italic.ttf',None),('EBGaramond-Italic[wght].ttf',600),('CrimsonPro-Italic[wght].ttf',600),('SourceSerif4-Italic[opsz,wght].ttf',600)],sys.argv[3]+'/serif.png',58)
sheet(R+'/t_1.5.png',(100,180,640,280),'DEALING WITH',[('Oswald[wght].ttf',500),('Oswald[wght].ttf',600),('BebasNeue-Regular.ttf',None),('LeagueGothic[wdth].ttf',None),('Anton-Regular.ttf',None)],sys.argv[3]+'/cond.png',58)
sheet(R+'/c_0.6.png',(150,600,600,680),'Feeling stuffy,',[('Nunito[wght].ttf',700),('Nunito[wght].ttf',600),('Poppins-Medium.ttf',None),('Poppins-SemiBold.ttf',None),('Montserrat[wght].ttf',600),('VarelaRound-Regular.ttf',None),('Figtree[wght].ttf',600),('PlusJakartaSans[wght].ttf',600),('Inter[opsz,wght].ttf',600)],sys.argv[3]+'/caps.png',40)
