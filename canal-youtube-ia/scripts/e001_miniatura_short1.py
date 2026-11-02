import sys, math
FONT = sys.argv[1]; variante = sys.argv[2]; out = sys.argv[3]
INK="#14161F"; BONE="#F6F0E4"; RED="#B3272D"; GOLD="#D9A637"; WOOD="#6B4A2B"; WOOD2="#4A321C"
def wheel(cx,cy,r):
    s=[f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BONE}" stroke-width="14"/>',
       f'<circle cx="{cx}" cy="{cy}" r="{r*0.18}" fill="{WOOD}" stroke="{BONE}" stroke-width="10"/>']
    for i in range(10):
        a=math.pi*2*i/10
        s.append(f'<line x1="{cx+math.cos(a)*r*0.18:.1f}" y1="{cy+math.sin(a)*r*0.18:.1f}" x2="{cx+math.cos(a)*r:.1f}" y2="{cy+math.sin(a)*r:.1f}" stroke="{BONE}" stroke-width="8"/>')
    return "".join(s)
def smoke(x,y,s,op=0.85):
    pts=[(0,0,1),(0.8,-0.5,0.8),(1.5,0.1,0.9),(0.6,0.6,0.75),(-0.7,0.4,0.7),(-0.4,-0.7,0.65)]
    return "".join(f'<circle cx="{x+dx*s:.0f}" cy="{y+dy*s:.0f}" r="{rr*s:.0f}" fill="{BONE}" opacity="{op}" stroke="{INK}" stroke-width="6"/>' for dx,dy,rr in pts)
textos = {
 "A": f'''<text x="540" y="235" text-anchor="middle" font-family="Anton" font-size="120" fill="{GOLD}" letter-spacing="8">1842</text>
 <text x="540" y="470" text-anchor="middle" font-family="Anton" font-size="245" fill="{BONE}" stroke="{INK}" stroke-width="16" paint-order="stroke">¡CON</text>
 <text x="540" y="680" text-anchor="middle" font-family="Anton" font-size="190" fill="{RED}" stroke="{INK}" stroke-width="14" paint-order="stroke">CAÑONAZOS!</text>''',
 "B": f'''<text x="540" y="215" text-anchor="middle" font-family="Anton" font-size="115" fill="{GOLD}" letter-spacing="8">1842</text>
 <text x="540" y="490" text-anchor="middle" font-family="Anton" font-size="300" fill="{BONE}" stroke="{INK}" stroke-width="18" paint-order="stroke">ES</text>
 <text x="540" y="745" text-anchor="middle" font-family="Anton" font-size="270" fill="{RED}" stroke="{INK}" stroke-width="18" paint-order="stroke">REAL</text>''',
}
sello = '' if variante=="B" else f'''<g transform="translate(300 1665) rotate(-8)">
  <rect x="-190" y="-78" width="380" height="140" rx="10" fill="none" stroke="{RED}" stroke-width="12"/>
  <rect x="-174" y="-62" width="348" height="108" rx="6" fill="none" stroke="{RED}" stroke-width="4"/>
  <text x="0" y="28" text-anchor="middle" font-family="Anton" font-size="96" fill="{RED}" letter-spacing="6">VERDAD</text></g>'''
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
<defs>
 <radialGradient id="luz" cx="50%" cy="58%" r="55%"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.38"/><stop offset="0.55" stop-color="{GOLD}" stop-opacity="0.08"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
 <filter id="grano"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 0.95  0 0 0 0 0.92  0 0 0 0 0.85  0 0 0 0.10 0"/></filter>
 <radialGradient id="vin" cx="50%" cy="50%" r="75%"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient>
</defs>
<rect width="1080" height="1920" fill="{INK}"/>
<rect width="1080" height="1920" fill="url(#luz)"/>
<!-- humo de cañones al fondo -->
{smoke(150,980,95)}{smoke(930,860,70,0.6)}
<!-- cañón izquierdo -->
<g transform="translate(120 1330) rotate(-28)"><rect x="-20" y="-34" width="260" height="68" rx="30" fill="{WOOD2}" stroke="{BONE}" stroke-width="10"/><circle cx="245" cy="0" r="30" fill="{INK}" stroke="{BONE}" stroke-width="10"/></g>
{wheel(150,1395,62)}
<!-- suelo -->
<line x1="0" y1="1460" x2="1080" y2="1460" stroke="{BONE}" stroke-width="8" opacity="0.5"/>
<!-- cureña -->
<rect x="250" y="1225" width="520" height="38" rx="8" fill="{WOOD}" stroke="{BONE}" stroke-width="10"/>
<line x1="250" y1="1245" x2="190" y2="1300" stroke="{BONE}" stroke-width="12"/>
{wheel(360,1350,108)}{wheel(660,1350,108)}
<!-- ataúd: tapa abierta apoyada -->
<polygon points="255,1180 300,1010 370,985 345,1160" fill="{WOOD2}" stroke="{BONE}" stroke-width="10" stroke-linejoin="round"/>
<!-- ataúd: interior (vista superior) -->
<polygon points="300,1150 390,1100 760,1112 760,1160 390,1190" fill="#2a1d12" stroke="{BONE}" stroke-width="10" stroke-linejoin="round"/>
<!-- pierna saliendo del ataúd -->
<g stroke-linecap="round" stroke-linejoin="round">
 <line x1="520" y1="1150" x2="585" y2="1025" stroke="{BONE}" stroke-width="30"/>
 <line x1="585" y1="1025" x2="570" y2="905" stroke="{BONE}" stroke-width="30"/>
 <circle cx="585" cy="1025" r="17" fill="{BONE}"/>
 <path d="M538 930 L540 800 L600 800 L602 868 L668 880 Q690 886 688 912 L686 932 Z" fill="#0b0b0f" stroke="{BONE}" stroke-width="9"/>
 <line x1="540" y1="828" x2="600" y2="828" stroke="{GOLD}" stroke-width="8"/>
 <circle cx="534" cy="922" r="10" fill="{GOLD}"/>
</g>
<!-- ataúd: frente -->
<polygon points="300,1150 390,1190 760,1160 760,1225 390,1235 300,1205" fill="{WOOD}" stroke="{BONE}" stroke-width="10" stroke-linejoin="round"/>
<line x1="420" y1="1212" x2="720" y2="1200" stroke="{GOLD}" stroke-width="6"/>
<!-- Santa Anna -->
<g stroke-linecap="round" stroke-linejoin="round">
 <line x1="880" y1="1090" x2="880" y2="1270" stroke="{BONE}" stroke-width="16"/>
 <line x1="845" y1="1095" x2="915" y2="1095" stroke="{BONE}" stroke-width="14"/>
 <line x1="845" y1="1100" x2="910" y2="1255" stroke="{RED}" stroke-width="22"/>
 <line x1="880" y1="1270" x2="840" y2="1460" stroke="{BONE}" stroke-width="16"/>
 <line x1="880" y1="1270" x2="905" y2="1365" stroke="{BONE}" stroke-width="16"/>
 <line x1="905" y1="1365" x2="920" y2="1460" stroke="#8a5a2b" stroke-width="20"/>
 <line x1="845" y1="1100" x2="830" y2="1270" stroke="{BONE}" stroke-width="14"/>
 <line x1="890" y1="1250" x2="985" y2="1330" stroke="{GOLD}" stroke-width="8"/>
 <line x1="915" y1="1100" x2="975" y2="1050" stroke="{BONE}" stroke-width="14"/>
 <line x1="975" y1="1050" x2="925" y2="985" stroke="{BONE}" stroke-width="14"/>
 <rect x="826" y="1080" width="36" height="18" rx="4" fill="{GOLD}"/><rect x="898" y="1080" width="36" height="18" rx="4" fill="{GOLD}"/>
 <path d="M828 1098 v14 M836 1098 v14 M844 1098 v14 M852 1098 v14 M900 1098 v14 M908 1098 v14 M916 1098 v14 M924 1098 v14" stroke="{GOLD}" stroke-width="4"/>
 <circle cx="880" cy="1015" r="62" fill="{INK}" stroke="{BONE}" stroke-width="14"/>
 <path d="M852 1012 q10 -8 20 0 M890 1012 q10 -8 20 0" fill="none" stroke="{BONE}" stroke-width="7"/>
 <path d="M866 1050 q14 -8 28 0" fill="none" stroke="{BONE}" stroke-width="7"/>
 <path d="M902 1028 q6 12 0 18 q-6 -6 0 -18" fill="#5aa9d6"/>
 <path d="M836 990 v40 M924 990 v40" stroke="{BONE}" stroke-width="8"/>
 <path d="M780 975 Q880 890 985 975 Q880 950 780 975 Z" fill="#0b0b0f" stroke="{GOLD}" stroke-width="7"/>
 <circle cx="880" cy="938" r="14" fill="{RED}" stroke="{GOLD}" stroke-width="4"/>
</g>
{textos[variante]}
{sello}
<rect width="1080" height="1920" filter="url(#grano)"/>
<rect width="1080" height="1920" fill="url(#vin)"/>
</svg>'''
html=f'''<!doctype html><html><head><meta charset="utf-8"><style>@font-face{{font-family:Anton;src:url("file://{FONT}")}}html,body{{margin:0;background:{INK}}}</style></head><body>{svg}</body></html>'''
open(out,'w').write(html)
