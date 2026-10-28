"""Genera los PDF del proyecto en reporte/:

- reporte: 00-REPORTE-COMPLETO.md -> Reporte-completo-canal-youtube-IA.pdf
- ideas:   15-ideas-virales-plan-30-dias.md -> Ideas-virales-y-plan-30-dias.pdf

Convierte el markdown en HTML con la identidad visual de la fase 6
(paleta, Anton / Fraunces / Inter), lo imprime con Chromium (Playwright de Node)
y le añade la portada. El índice lleva números de página: se imprime dos veces,
la primera para localizar en qué página cae cada sección.

Requisitos: markdown-it-py y pypdf (pip), Node con Playwright y Chromium.
Uso: python3 scripts/reporte_pdf.py [--doc reporte|ideas] [carpeta_de_fuentes]
     La carpeta de fuentes debe tener local.css con los @font-face de Google Fonts.
     Sin ella se usan las fuentes del sistema.
"""
import argparse
import base64
import html
import re
import subprocess
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt
from pypdf import PdfReader, PdfWriter

RAIZ = Path(__file__).resolve().parent.parent
CIFRAS_REPORTE = (
    '<div class="cifras">'
    '<div><b>79,2 / 100</b><span>Puntuación del nicho recomendado (matriz de 6 opciones)</span></div>'
    '<div><b>8.000 h</b><span>Horas para entrar al Programa de Socios desde el 1-feb-2027 (hoy 4.000)</span></div>'
    '<div><b>≈ 41 USD</b><span>Costo mensual de la pila inicial de herramientas</span></div>'
    '<div><b>6 + 15</b><span>Videos largos y Shorts del plan de 90 días</span></div></div>')
CIFRAS_IDEAS = (
    '<div class="cifras">'
    '<div><b>107.000</b><span>Mediana de vistas por Short de Squire Explains, el canal más rápido de la muestra</span></div>'
    '<div><b>11,7 M</b><span>Vistas de sus 32 Shorts en unas 4 semanas (10.000 suscriptores el día 26)</span></div>'
    '<div><b>26 + 2</b><span>Shorts y videos largos del plan de 30 días</span></div>'
    '<div><b>31-ene-2027</b><span>Último día para entrar al Programa de Socios con 10 M de vistas de Shorts (luego 20 M)</span></div></div>')
DOCUMENTOS = {
    "reporte": dict(
        md=RAIZ / "00-REPORTE-COMPLETO.md",
        salida=RAIZ / "reporte" / "Reporte-completo-canal-youtube-IA.pdf",
        titulo="Reporte completo",
        pie="Canal de YouTube con IA · Reporte completo · 27-oct-2026",
        cifras=CIFRAS_REPORTE,
        portada=dict(sello="EXPEDIENTE N.º 001", kicker="Reporte completo · 14 entregables",
                     titulo="Canal de YouTube<br>automatizado con IA",
                     sub="Investigación de 8 canales, nicho recomendado, identidad visual, sistema de producción, "
                         "monetización, plan de 90 días y dashboard de seguimiento.",
                     fecha="27 de octubre de 2026"),
        meta={"/Title": "Reporte completo: canal de YouTube con IA",
              "/Subject": "14 entregables: investigación, nicho, marca, producción, monetización, plan y dashboard"}),
    "ideas": dict(
        md=RAIZ / "15-ideas-virales-plan-30-dias.md",
        salida=RAIZ / "reporte" / "Ideas-virales-y-plan-30-dias.pdf",
        titulo="Ideas virales y plan de 30 días",
        pie="Canal de YouTube con IA · Ideas virales y plan de 30 días · 28-oct-2026",
        cifras=CIFRAS_IDEAS,
        portada=dict(sello="EXPEDIENTE N.º 002", kicker="Ideas de canal · plan de 30 días",
                     titulo="Historias reales<br>que parecen inventadas",
                     sub="Seis ideas de canal con potencial viral para público adulto, la idea ganadora en detalle, "
                         "30 historias para el primer mes y un plan de 30 días hacia la monetización.",
                     fecha="28 de octubre de 2026"),
        meta={"/Title": "Ideas virales y plan de 30 días",
              "/Subject": "Ideas de canal con potencial viral, idea ganadora y plan de 30 días"}),
}
REPO_URL = "https://github.com/camilocaicedo0802-cmd/Claude/blob/claude/youthful-newton-zzmr1m/canal-youtube-ia/"

RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [,, entrada, salida, conPie, textoPie] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + entrada, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const pie = `<div style="width:100%;font-family:Inter,Arial,sans-serif;font-size:7.5px;color:#7a6f60;
      padding:0 16mm;display:flex;justify-content:space-between;">
      <span>${textoPie || ''}</span>
      <span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  await page.pdf({
    path: salida, format: 'A4', printBackground: true,
    displayHeaderFooter: conPie === '1',
    headerTemplate: '<div></div>', footerTemplate: pie,
    margin: conPie === '1' ? { top: '16mm', bottom: '16mm', left: '16mm', right: '16mm' }
                           : { top: '0', bottom: '0', left: '0', right: '0' },
  });
  await browser.close();
})();
"""

CSS = """
:root{--noche:#14161F;--tinta:#1E1A16;--amate:#EADBC0;--hueso:#F6F0E4;--cochinilla:#B3272D;
--maya:#3D8DB5;--oro:#D9A637;--selva:#2E5B45;--gris:#6b6257;}
*{box-sizing:border-box}
html{font-size:10pt}
body{margin:0;font-family:Inter,Arial,sans-serif;color:var(--tinta);line-height:1.45;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,h3{font-family:Fraunces,Georgia,serif;color:var(--noche);line-height:1.15}
h1{font-size:2.1rem;margin:0 0 .4rem}
h2{font-size:1.55rem;margin:0 0 .7rem;padding-top:.2rem;break-before:page;break-after:avoid}
h2 .num{font-family:Anton,Impact,sans-serif;color:var(--cochinilla);font-weight:400;letter-spacing:.02em;
  display:block;font-size:.8rem;text-transform:uppercase;margin-bottom:.15rem}
h3{font-size:1.12rem;margin:1.1rem 0 .4rem;break-after:avoid}
p{margin:.35rem 0 .55rem}
p:has(+ ul),p:has(+ ol),p:has(+ table){break-after:avoid}
ul,ol{margin:.3rem 0 .6rem;padding-left:1.25rem}
li{margin:.12rem 0}
li>ul,li>ol{margin:.15rem 0}
strong{font-weight:600;color:#000}
em{font-family:Fraunces,Georgia,serif}
a{color:var(--maya);text-decoration:none}
code{font-family:Inter,Arial,sans-serif;font-size:.92em;background:none;color:var(--maya)}
hr{border:0;border-top:1px solid #d8ccb4;margin:1rem 0}
table{width:100%;border-collapse:collapse;margin:.5rem 0 .9rem;font-size:.86rem;line-height:1.32}
thead{display:table-header-group}
th{background:var(--noche);color:var(--hueso);font-weight:600;text-align:left;padding:.35rem .4rem;vertical-align:bottom}
td{padding:.3rem .4rem;border-bottom:1px solid #e3d8c3;vertical-align:top}
tr{break-inside:avoid}
tbody tr:nth-child(even) td{background:#faf6ee}
blockquote{margin:.6rem 0;padding:.5rem .8rem;background:var(--hueso);border-left:4px solid var(--cochinilla)}
.lead{background:var(--hueso);border-left:4px solid var(--oro);padding:.6rem .9rem;margin:.4rem 0 1rem}
.lead p{margin:.25rem 0}
figure{margin:.6rem 0 1rem;break-inside:avoid}
figure img{width:100%;display:block;border:1px solid #d8ccb4}
figcaption{font-size:.8rem;color:var(--gris);margin-top:.25rem}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.45rem}
.cifras{display:grid;grid-template-columns:repeat(4,1fr);gap:.45rem;margin:.2rem 0 .9rem}
.cifras div{background:var(--noche);color:var(--hueso);padding:.55rem .6rem;border-top:3px solid var(--oro)}
.cifras b{display:block;font-family:Anton,Impact,sans-serif;font-weight:400;font-size:1.55rem;color:var(--hueso);letter-spacing:.01em}
.cifras span{font-size:.78rem;color:var(--amate);line-height:1.25;display:block;margin-top:.1rem}
.toc{margin-top:1.4rem}
.toc h2{break-before:avoid}
.toc ol{list-style:none;padding:0;margin:0}
.toc li{display:flex;align-items:baseline;gap:.4rem;padding:.32rem 0;border-bottom:1px dotted #cdbfa5;font-size:1rem}
.toc li .t{flex:1}
.toc li .n{font-family:Anton,Impact,sans-serif;color:var(--cochinilla);min-width:2.2rem;text-align:right}
.toc li .k{font-family:Anton,Impact,sans-serif;color:var(--gris);min-width:2.2rem}
.nota{font-size:.82rem;color:var(--gris)}
"""

PORTADA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{fuentes}
@page{{size:A4;margin:0}}
html,body{{margin:0;height:100%}}
body{{background:#14161F;color:#F6F0E4;font-family:Inter,Arial,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.p{{position:relative;width:210mm;height:297mm;padding:24mm 20mm;overflow:hidden}}
.franja{{position:absolute;left:0;right:0;bottom:0;height:10mm;display:flex}}
.franja div{{flex:1}}
.sello{{display:inline-block;font-family:Anton,Impact,sans-serif;color:#B3272D;border:2.5px solid #B3272D;
  padding:2mm 4mm;letter-spacing:.08em;font-size:13pt;transform:rotate(-4deg);margin-bottom:14mm}}
.k{{font-family:Anton,Impact,sans-serif;letter-spacing:.06em;color:#D9A637;font-size:12pt;text-transform:uppercase}}
h1{{font-family:Fraunces,Georgia,serif;font-weight:700;font-size:40pt;line-height:1.04;margin:4mm 0 8mm;color:#F6F0E4}}
.sub{{font-family:Fraunces,Georgia,serif;font-style:italic;font-size:15pt;line-height:1.35;color:#EADBC0;max-width:150mm}}
.marca{{margin-top:22mm;padding-top:8mm;border-top:1px solid #3a3a46;max-width:160mm}}
.marca .n{{font-family:Anton,Impact,sans-serif;font-size:26pt;letter-spacing:.02em;color:#F6F0E4}}
.marca .e{{font-size:12pt;color:#EADBC0;margin-top:1mm}}
.meta{{position:absolute;left:20mm;right:20mm;bottom:22mm;font-size:9.5pt;color:#b8ad9a;line-height:1.6}}
.meta b{{color:#F6F0E4;font-weight:600}}
</style></head><body><div class="p">
<div class="sello">{sello}</div>
<div class="k">{kicker}</div>
<h1>{titulo}</h1>
<div class="sub">{sub}</div>
<div class="marca"><div class="k" style="color:#b8ad9a;font-size:9pt">Propuesta de marca</div>
<div class="n">VERDAD DE LEYENDA</div>
<div class="e">“Con fuentes. Sin cuentos.” · Historia y leyendas de Latinoamérica, en español neutro</div></div>
<div class="meta"><b>Fecha:</b> {fecha}<br>
<b>Datos y documentos de detalle:</b> repositorio del proyecto, carpeta <i>canal-youtube-ia</i>
(rama claude/youthful-newton-zzmr1m)<br>
<b>Etiquetas:</b> dato = medido con fuente · estimación = cálculo con supuesto explícito · hipótesis = a validar</div>
<div class="franja"><div style="background:#B3272D"></div><div style="background:#D9A637"></div>
<div style="background:#3D8DB5"></div><div style="background:#2E5B45"></div><div style="background:#EADBC0"></div></div>
</div></body></html>"""


def imagen(ruta):
    datos = base64.b64encode(ruta.read_bytes()).decode()
    return f"data:image/png;base64,{datos}"


def figuras_marca():
    m = RAIZ / "marca"
    return f"""
<figure><img src="{imagen(m / 'paleta.png')}" alt="Paleta de la marca">
<figcaption>Paleta propuesta (fase 6): ocho pigmentos históricos americanos.</figcaption></figure>
<div class="grid">
<figure><img src="{imagen(m / 'miniatura_concepto_1_llorona.png')}" alt="Concepto de miniatura: La Llorona">
<figcaption>Concepto 1 · La Llorona: “¿EXISTIÓ?”</figcaption></figure>
<figure><img src="{imagen(m / 'miniatura_concepto_2_colombia.png')}" alt="Concepto de miniatura: Colombia">
<figcaption>Concepto 2 · Colombia: “¿POR QUÉ ÉL?”</figcaption></figure>
<figure><img src="{imagen(m / 'miniatura_concepto_3_tenochtitlan.png')}" alt="Concepto de miniatura: Tenochtitlan">
<figcaption>Concepto 3 · Tenochtitlan: “VIVÍAS AQUÍ”</figcaption></figure>
</div>
<p class="nota">Bocetos de composición generados por código (scripts/marca_bocetos.py) con tipografía provisional.
No son las miniaturas finales: muestran la regla 1-2-3, la paleta y los sellos de serie.</p>"""


def md_a_html(texto):
    md = MarkdownIt("commonmark", {"html": False, "typographer": False}).enable("table")
    cuerpo = md.render(texto)
    # Enlaces relativos del repositorio -> GitHub (rama del proyecto)
    cuerpo = re.sub(r'href="(?!https?://|#)([^"]+)"', lambda m: f'href="{REPO_URL}{m.group(1)}"', cuerpo)
    return cuerpo


def preparar_secciones(cuerpo, cifras):
    """Quita el h1 y el bloque inicial, numera los h2 y devuelve la lista para el índice."""
    cuerpo = re.sub(r"<h1>.*?</h1>", "", cuerpo, count=1, flags=re.S)
    partes = re.split(r"(?=<h2>)", cuerpo, maxsplit=1)
    intro, resto = (partes[0], partes[1]) if len(partes) == 2 else ("", cuerpo)
    secciones = []

    def numerar(m):
        texto = html.unescape(re.sub("<[^>]+>", "", m.group(1)))
        n = len(secciones) + 1
        ancla = f"s{n}"
        mm = re.match(r"((?:Entregable|Parte) \d+)\. (.*)", texto)
        if mm:
            etiqueta, titulo = mm.group(1), mm.group(2)
        else:
            etiqueta, titulo = "", texto
        secciones.append((ancla, etiqueta, titulo))
        num = f'<span class="num">{etiqueta}</span>' if etiqueta else ""
        return f'<h2 id="{ancla}">{num}{html.escape(titulo)}</h2>'

    resto = re.sub(r"<h2>(.*?)</h2>", numerar, resto)
    resto = resto.replace("</h2>", "</h2>" + cifras, 1)
    # quitar los <hr> que separaban secciones (cada h2 ya abre página)
    resto = re.sub(r"<hr\s*/?>", "", resto)
    intro = re.sub(r"<hr\s*/?>", "", intro)
    return intro, resto, secciones


def indice(secciones, paginas=None):
    filas = []
    for i, (ancla, etiqueta, titulo) in enumerate(secciones):
        n = str(paginas[i]) if paginas and paginas[i] else "00"
        k = etiqueta.replace("Entregable ", "E").replace("Parte ", "P") if etiqueta else ""
        filas.append(f'<li><span class="k">{k}</span><a class="t" href="#{ancla}">{html.escape(titulo)}</a>'
                     f'<span class="n">{n}</span></li>')
    return f'<section class="toc"><h2 style="break-before:avoid">Índice</h2><ol>{"".join(filas)}</ol></section>'


def documento(fuentes_css, intro, toc, resto, titulo):
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
            f'<style>{fuentes_css}{CSS}</style></head><body>'
            f'<section><h1>{titulo}</h1><div class="lead">{intro}</div></section>'
            f'{toc}{resto}</body></html>')


def imprimir(html_texto, destino, con_pie, carpeta, pie=""):
    entrada = carpeta / f"{destino.stem}.html"
    entrada.write_text(html_texto, encoding="utf-8")
    js = carpeta / "render.js"
    js.write_text(RENDER_JS, encoding="utf-8")
    subprocess.run(["node", str(js), str(entrada), str(destino), "1" if con_pie else "0", pie], check=True)


def paginas_de_secciones(pdf, secciones):
    lector = PdfReader(str(pdf))
    textos = [re.sub(r"\s+", " ", p.extract_text() or "") for p in lector.pages]
    res = []
    # las secciones empiezan después de la página del índice
    desde = next((i + 1 for i, t in enumerate(textos) if "Índice" in t[:120]), 0)
    for _, etiqueta, titulo in secciones:
        patron = re.escape(etiqueta) + r"\b" if etiqueta else re.escape(titulo[:40])
        encontrado = None
        for i in range(desde, len(textos)):
            if re.search(patron, textos[i][:160], re.IGNORECASE):
                encontrado = i
                break
        # número de página del cuerpo (el mismo que imprime el pie; la portada no se numera)
        res.append(encontrado + 1 if encontrado is not None else None)
        if encontrado is not None:
            desde = encontrado + 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fuentes", nargs="?", help="carpeta con local.css de Google Fonts")
    ap.add_argument("--doc", choices=sorted(DOCUMENTOS), default="reporte")
    args = ap.parse_args()
    cfg = DOCUMENTOS[args.doc]
    carpeta_fuentes = Path(args.fuentes) if args.fuentes else None
    fuentes_css = ""
    if carpeta_fuentes and (carpeta_fuentes / "local.css").exists():
        css = (carpeta_fuentes / "local.css").read_text()
        fuentes_css = re.sub(r"url\(([^)]+\.woff2)\)",
                             lambda m: f"url(file://{carpeta_fuentes.resolve() / m.group(1)})", css)

    texto = cfg["md"].read_text(encoding="utf-8")
    cuerpo = md_a_html(texto)
    intro, resto, secciones = preparar_secciones(cuerpo, cfg["cifras"])
    # Bocetos de marca al final del entregable 7, antes del entregable 8
    pos = resto.find(">Entregable 8<")
    if pos != -1:
        inicio = resto.rfind("<h2", 0, pos)
        resto = resto[:inicio] + figuras_marca() + resto[inicio:]

    salida = cfg["salida"]
    salida.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cuerpo_pdf = tmp / "cuerpo.pdf"
        imprimir(documento(fuentes_css, intro, indice(secciones), resto, cfg["titulo"]), cuerpo_pdf, True, tmp, cfg["pie"])
        paginas = paginas_de_secciones(cuerpo_pdf, secciones)
        imprimir(documento(fuentes_css, intro, indice(secciones, paginas), resto, cfg["titulo"]),
                 cuerpo_pdf, True, tmp, cfg["pie"])
        portada_pdf = tmp / "portada.pdf"
        imprimir(PORTADA.format(fuentes=fuentes_css, **cfg["portada"]), portada_pdf, False, tmp)

        escritor = PdfWriter()
        for p in PdfReader(str(portada_pdf)).pages[:1]:
            escritor.add_page(p)
        for p in PdfReader(str(cuerpo_pdf)).pages:
            escritor.add_page(p)
        escritor.add_metadata({**cfg["meta"], "/Author": "Proyecto canal-youtube-ia"})
        with salida.open("wb") as fh:
            escritor.write(fh)
    print(salida, "páginas por sección:", paginas)


if __name__ == "__main__":
    main()
