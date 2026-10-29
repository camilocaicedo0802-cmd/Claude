"""Guion de planos del piloto E001 (bloques 1 a 3) para Nano Banana / Google Flow.

Genera:
- video/E001/planos_piloto.json  (para el montaje automático)
- guiones/E001-piloto-prompts-nano-banana.md  (para pegar en Flow o usar por API)
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ESTILO_PAPEL = (
    "Minimalist stick-figure illustration in the style of an animated history explainer: "
    "round heads, single thick black ink lines for bodies and limbs, simple dot eyes, flat colors only. "
    "Background of aged parchment paper with subtle fibers and a soft vignette, warm tone close to #EADBC0. "
    "Limited accent palette used sparingly: crimson red #B3272D, antique gold #D9A637, muted blue #3D8DB5, deep green #2E5B45. "
    "Adult, documentary mood with a touch of dry humor. Clean composition with generous empty space for text overlays. "
    "16:9 widescreen. No text, no letters, no numbers, no watermark, no logos."
)
ESTILO_NOCHE = (
    "Minimalist stick-figure illustration in the style of an animated history explainer: "
    "round heads, single thick off-white chalk-like lines (#F6F0E4) for bodies and limbs, simple dot eyes, flat colors only. "
    "Background of very dark ink navy (#14161F) with faint paper grain and a soft spotlight. "
    "Accents used sparingly: crimson red #B3272D and antique gold #D9A637. "
    "Adult, mysterious documentary mood. Clean composition with generous empty space for text overlays. "
    "16:9 widescreen. No text, no letters, no numbers, no watermark, no logos."
)
SANTA_ANNA = (
    "General Santa Anna as a stick figure: round head with short dark sideburns, a black bicorne hat with thin gold trim "
    "worn sideways, gold fringed epaulettes on both shoulders, a crimson sash across the chest and a small saber at the hip. "
    "Proud, theatrical posture. Adult proportions (taller and slimmer than a cartoon child)."
)

PLANOS = [
    # id, bloque, frase (inicio de la narración que cubre), estilo, escena, texto_en_pantalla, movimiento, con_referencia
    ("REF", "-", "Hoja de personaje (generar primero; se usa como referencia)", "papel",
     f"A character reference sheet showing the same character three times side by side: standing proud, saluting, "
     f"and pointing forward. {SANTA_ANNA} Plain parchment background, evenly spaced, full body.",
     "", "-", False),
    ("S01", "B1", "México, mil ochocientos cuarenta y dos.", "noche",
     "A wide establishing shot of the silhouette of 1840s Mexico City at dawn: the twin bell towers of a large cathedral, "
     "low colonial rooftops and a few church domes along the bottom third. The upper two thirds are empty dark sky.",
     "1842 · MÉXICO", "acercamiento lento", False),
    ("S02", "B1", "Hay desfile,", "papel",
     "A side view of a military parade: a long row of stick-figure soldiers marching left to right in step, "
     "each wearing a tall dark shako hat and carrying a rifle on the shoulder; two of them carry plain vertical "
     "green-white-red tricolor flags. A cathedral silhouette faintly in the background.",
     "", "paneo izquierda → derecha", False),
    ("S03", "B1", "hay cañonazos,", "papel",
     "Two antique bronze cannons on wooden carriages firing a ceremonial salute, each releasing a big round puff of white smoke "
     "drawn as stacked circles. Stick-figure gunners stand beside them covering their ears.",
     "SALVAS DE CAÑÓN", "sacudida + acercamiento", False),
    ("S04", "B1", "hay discursos...", "papel",
     "A stick-figure orator in a top hat on a wooden podium decorated with a tricolor ribbon, one arm raised dramatically, "
     "addressing a crowd of stick figures in top hats and shawls seen from behind in the foreground.",
     "", "acercamiento al orador", False),
    ("S05", "B1", "para enterrar una pierna.", "papel",
     "A small wooden coffin resting on a gun carriage in a solemn procession. The lid is open just enough to show that "
     "inside there is only a single stick-figure leg wearing a black military boot. Two stick-figure soldiers salute beside it "
     "with serious faces. Solemn yet absurd mood.",
     "¿UNA PIERNA?", "acercamiento al ataúd", False),
    ("S06", "B1", "No es una metáfora. Es la pierna de Antonio López de Santa Anna.", "noche",
     f"A centered full-body portrait of {SANTA_ANNA} He stands on a low stone step under a single spotlight, "
     "hand on chest, chin up. Empty dark space on the left and right.",
     "ANTONIO LÓPEZ DE SANTA ANNA · NO ES UNA METÁFORA", "acercamiento lento", True),
    ("S07", "B1", "Soldados formados.", "papel",
     "A front view of a straight line of identical stick-figure soldiers standing at attention, tall dark shako hats, "
     "rifles held upright, perfectly symmetrical composition.",
     "", "paneo lateral corto", False),
    ("S08", "B1", "Versos escritos para la ocasión.", "papel",
     "A stick-figure poet with a quill pen writing on a very long paper scroll that unrolls off the table onto the floor, "
     "a single candle on the desk, inspired dreamy expression.",
     "", "acercamiento a la pluma", False),
    ("S09", "B1", "Un monumento esperándola.", "papel",
     "A tall stone column monument in an old cemetery with a small decorative urn on top. A few stick figures at the base "
     "look up at it in awe. Cypress trees on both sides.",
     "", "paneo de abajo hacia arriba", False),
    ("S10", "B1", "Y ese funeral ni siquiera es lo más raro.", "noche",
     f"{SANTA_ANNA} He is frozen mid-salute with a startled expression, as if the music just stopped. "
     "Placed on the right third of the frame, the rest is dark empty space.",
     "NI SIQUIERA ES LO MÁS RARO", "corte seco + leve sacudida", True),
    ("S11", "B1", "Otra pierna suya sigue hoy en una vitrina.", "noche",
     "A modern museum display case made of glass, lit from above by a single spotlight. Inside the case stands an antique "
     "prosthetic leg made of cork and wood with leather straps. A small blank label card at the base. Dark museum room.",
     "HOY · EN UNA VITRINA", "acercamiento a la vitrina", False),
    ("S12", "B1", "En Estados Unidos.", "código",
     "Mapa animado por código (no se genera imagen): México → flecha → Illinois.",
     "MÉXICO → ILLINOIS, EE. UU.", "dibujo de la flecha", False),
    ("S13", "B1", "Quédate, porque al final vas a saber cuál de las dos tuvo el destino más absurdo.", "papel",
     "Two legs displayed side by side like museum exhibits, separated by a thin vertical ink line: on the left a pale silhouette "
     "of a human leg with a large question mark floating above it, on the right the antique cork-and-wood prosthetic leg "
     "with leather straps. Symmetrical composition.",
     "¿CUÁL TUVO EL DESTINO MÁS ABSURDO?", "acercamiento lento", False),
    ("S14", "B2", "Seguro el nombre de Santa Anna te suena.", "papel",
     f"{SANTA_ANNA} He stands on a stone pedestal in a town square. Below, a crowd of stick figures is split in two: "
     "the left half cheers with raised arms, the right half boos with thumbs down.",
     "¿HÉROE? · ¿VILLANO?", "paneo izquierda → derecha", True),
    ("S15", "B2", "Pero esta parte casi nadie la cuenta completa.", "papel",
     "An old history textbook lying open on a wooden desk, seen from above. One page has been torn out, leaving a ragged "
     "edge and an obvious gap in the book.",
     "LA PARTE QUE FALTA", "acercamiento al hueco", False),
    ("S16", "B2", "Y no es un chisme de internet.", "papel",
     "A stick figure holding a modern smartphone and frowning skeptically at the screen, which shows only abstract chat "
     "bubbles and an exclamation mark.",
     "¿CHISME DE INTERNET? → NO", "leve acercamiento", False),
    ("S17", "B2", "Está en periódicos de la época, en biografías serias y en la ficha de un museo.", "papel",
     "A top-down view of evidence laid out on a wooden desk: a folded 1840s newspaper with columns of illegible squiggles, "
     "a thick leather-bound biography book and a small museum label card, arranged with space between them.",
     "PERIÓDICOS 1842 · BIOGRAFÍAS · MUSEO", "paneo cenital", False),
    ("S18", "B2", "Lo que no está del todo claro, también te lo voy a decir.", "papel",
     "A large brass magnifying glass hovering over an old handwritten document. Under the lens, an ink blot forms the shape "
     "of a question mark.",
     "CON FUENTES. SIN CUENTOS.", "acercamiento + sello", False),
    ("S19", "B3", "Al terminar este video vas a saber cómo una pierna terminó enterrada con honores de héroe.", "papel",
     "A small wooden coffin draped with a tricolor ribbon and topped with a gold military medal, flanked by two stick-figure "
     "soldiers saluting. Simple, centered, solemn.",
     "1. EL FUNERAL", "acercamiento lento", False),
    ("S20", "B3", "Vas a entender por qué, dos años después, la misma ciudad la sacó de su tumba.", "noche",
     "The same stone column monument at night, its urn knocked over and empty. In the distance, a crowd of stick figures "
     "carrying torches walks away down a street.",
     "2. LA TUMBA VACÍA · 1844", "paneo lateral", False),
    ("S21", "B3", "Y vas a tener una historia que casi nadie conoce completa.", "papel",
     "Two adult stick figures sitting at a dinner table with coffee cups after a meal. One tells a story with both arms "
     "spread wide; the other leans back with jaw dropped in disbelief.",
     "3. UNA HISTORIA PARA CONTAR", "acercamiento lento", False),
    ("S22", "B3", "Al final, el veredicto: ¿verdad, a medias o mito?", "papel",
     "Three old wooden rubber stamps standing in a row on a desk, with ink pads in green, gold and crimson. "
     "The stamp faces are blank.",
     "VERDAD · A MEDIAS · MITO", "golpes de sello animados", False),
    ("S23", "B3", "Y después, una continuación todavía más extraña.", "noche",
     "A sealed old envelope with a crimson wax seal lying on a dark desk under a single spotlight.",
     "PRÓXIMO EXPEDIENTE", "acercamiento lento", False),
    ("S24", "B3", "Pero primero, conozcamos al dueño de la pierna.", "papel",
     f"{SANTA_ANNA} He walks in from the left side of the frame and tips his bicorne hat to the viewer with a confident smile. "
     "The right half of the frame is empty parchment.",
     "EXPEDIENTE: SANTA ANNA", "paneo siguiendo al personaje", True),
]


def prompt_completo(estilo, escena, con_ref):
    base = {"papel": ESTILO_PAPEL, "noche": ESTILO_NOCHE}.get(estilo, "")
    ref = ("Use the attached character reference image for General Santa Anna: keep the same hat, epaulettes, sash, "
           "saber and proportions. ") if con_ref else ""
    return f"{escena} {ref}{base}".strip()


def main():
    datos = []
    for (pid, bloque, frase, estilo, escena, texto, mov, ref) in PLANOS:
        datos.append(dict(id=pid, bloque=bloque, frase=frase, estilo=estilo, texto_en_pantalla=texto,
                          movimiento=mov, usa_referencia=ref,
                          prompt=prompt_completo(estilo, escena, ref) if estilo != "código" else None,
                          archivo=f"video/E001/img/{pid}.png" if estilo != "código" else None))
    (RAIZ / "video/E001").mkdir(parents=True, exist_ok=True)
    (RAIZ / "video/E001/planos_piloto.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")

    md = ["# E001: piloto (bloques 1 a 3), guion de planos y prompts para Nano Banana",
          "",
          "**Para qué sirve:** generar las imágenes del piloto de 90 segundos de \"Le hicieron un funeral de Estado a una pierna\".",
          "",
          "**Cómo usarlo**",
          "",
          "1. **Primero la hoja de personaje (`REF`).** Elige la mejor versión de Santa Anna; será la referencia de todos los planos que lo muestran.",
          "2. **Configuración:** formato 16:9, la resolución más alta disponible.",
          "3. **Planos marcados \"con referencia\":** adjunta la imagen `REF`. En Google Flow, súbela como ingrediente o imagen de referencia.",
          "4. **Nombre de los archivos:** guarda cada imagen con su código (`S01.png`, `S02.png`…) en `video/E001/img/`.",
          "5. **Textos, fechas, mapas y sellos:** no van en la imagen. Los añado yo en la edición con las tipografías de la marca. Por eso cada prompt pide \"no text\".",
          "",
          "**Estilo:** stickman de tinta sobre pergamino para la narración; fondo tinta noche con líneas color hueso para los momentos dramáticos. Paleta y tono de la marca (fase 6).",
          ""]
    for d in datos:
        md.append(f"## {d['id']} · {d['bloque']}")
        md.append("")
        md.append(f"- **Narración:** \"{d['frase']}\"")
        if d["texto_en_pantalla"]:
            md.append(f"- **Texto en pantalla (lo pongo yo):** {d['texto_en_pantalla']}")
        if d["movimiento"] != "-":
            md.append(f"- **Movimiento en la edición:** {d['movimiento']}")
        if d["prompt"]:
            md.append(f"- **Con referencia de Santa Anna:** {'sí' if d['usa_referencia'] else 'no'}")
            md.append("")
            md.append("```")
            md.append(d["prompt"])
            md.append("```")
        else:
            md.append("- **Imagen:** no hace falta; lo animo por código con un mapa real (Natural Earth, dominio público).")
        md.append("")
    (RAIZ / "guiones/E001-piloto-prompts-nano-banana.md").write_text("\n".join(md), encoding="utf-8")
    print(len([d for d in datos if d['prompt']]), "prompts")


if __name__ == "__main__":
    main()
