# Librería de SFX del cliente

Efectos de sonido entregados por el cliente (Drive: *SFX PACK 1* y *SFX PACK 2*). Son los únicos SFX que se
usan en los reels; los sonidos sintetizados del primer reel quedan descartados.

- 361 archivos en Drive → **184 sonidos únicos** (los duplicados se detectan por el audio, no por el nombre).
- La compilación *25 sonidos de transiciones* se separó en `whoosh/transicion_01…27`.
- Todo se convierte a WAV 48 kHz. El audio no se sube a este repositorio (son packs de terceros y viven en el Drive
  del cliente). Para reconstruir la librería: descarga la carpeta de SFX de Drive a una carpeta local y ejecuta

```bash
python3 video/sfx-library/build_library.py <carpeta_descargada> <salida>   # crea <salida>/audio/... y library.json
```

## Categorías (`library.json`)

| Categoría | Qué hay | Uso en los reels |
| --- | --- | --- |
| `typing` (25) | Mechanical Keyboard Click 01–19, Tecla, Escribir teclado, Type Digital, Efecto type de letras | **Cada texto que aparece**: un clic de tecla por palabra (o por letra en los títulos tecleados). Se alternan los clics 04–13 y 17–19 para que no suene repetido. |
| `whoosh` (61) | Swoosh 01, VS_Short Whoosh 1–8, Woosh Effect 2–14, Whips, Long Woosh, Transición 01–27 | Transiciones whip/zoom, entradas de títulos grandes. |
| `impact` (29) | Sub Bass Drop/Hit, Deep Bass Hit, Boom, Cinematic Bass, Grand Hit | Palabras clave (golpe grave suave), revelaciones, logo. |
| `riser` (8) | Riser, Sharp Riser, Riser Intense | Antes del before & after y del cierre. |
| `camera` (21) | Shutters, Camera Flash (simple/doble/triple) | Freeze frames, flashes de revelación. |
| `click` (10) | Mouse Click 01–04, Lighter Double Click, Camera Roll Click | Checks de listas, toques de UI. |
| `pop` (9) | Pop up SFX, Chasquido épico, notificación | Etiquetas y palabras que aparecen con pop. |
| `glass` (3) | Vidrio, Crash with glass, foco roto | "Glass doors". |
| `retro` (1) | Film Burns SFX | Efecto retro/película. |
| `marker` (4) | Rotulador, resaltador, bolígrafo | Subrayados. |
| `drone` (9) | Drones, viento, trueno | Ambientes (poco uso). |
| `misc` (4) | Contador, reloj, gota de agua, láser | Puntuales. |

También venían 4 marcos PNG *Rectángulos Super 8mm* (1080×1920 con ventana transparente) para el look retro, y
`0529.mp4`, un reel de ejemplo de otra marca (referencia, no efecto).
