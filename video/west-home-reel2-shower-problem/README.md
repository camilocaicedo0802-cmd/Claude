# West Home Improvement · Reel 2 — "Your bathroom isn't the problem"

Reel vertical de 35,8 s (1080×1920, 30 fps) para Instagram, con Félix y B-roll de proyectos reales.

**v2 (ajustes del cliente):**
- Sin silencios: se cortó la pausa de 0,8 s al inicio de la toma IMG_7832 (antes de "But your shower") y todas las tomas
  van seguidas con 80 ms entre una y otra. El bloque del catálogo (sin voz) bajó a 1,6 s. Los tiempos de la tabla de abajo
  son de la v1; la línea de tiempo ahora se calcula sola en `timeline.py` a partir de las tomas.
- **Ningún texto tapa a una persona**: `render.py` recorta a la persona en cada cuadro (U2-Net + guided filter) y la vuelve
  a poner encima de todos los textos y gráficos. Además, cada subtítulo se coloca solo en una zona libre: abajo si ahí no hay
  nadie, y si no, en el espacio sobre la cabeza (`free_y` en `overlays.py`).

## Estructura

| Tiempo | Voz | Imagen | Texto / efecto |
| --- | --- | --- | --- |
| 0–2,8 | Tulsa homeowners, your bathroom might not be outdated | Félix, zoom-in sutil | Hook tecleado: YOUR BATHROOM ISN'T THE PROBLEM… |
| 2,8–4,9 | Your shower might be the problem | Félix → ducha de fibra de vidrio vieja (P4) | YOUR **SHOWER** |
| 4,9–8,8 | Think about it… mirror, lighting, vanity | Félix → espejo, luces, vanity (P3) | Checklist que se marca |
| 8,8–11,8 | But your shower… from the 1990s | Baño antiguo (P3 Owasso, antes) | Drop de la música |
| 11,8–12,8 | (1990s) | Freeze frame retro: marco Super 8, grano, RGB split | 1990s + PLAY ▶ / JUN 14 1995, tape stop |
| 12,9–15,3 | The whole bathroom might feel outdated | Vanity antigua (P3, P6) | Sello OUTDATED |
| 15,4–18,8 | …shower transformations | Félix → **antes/después** del mismo baño (P4) | Barrido con línea, BEFORE/AFTER, SHOWER TRANSFORMATION en el drop |
| 18,8–20,1 | That makes a real difference | Félix dentro de la ducha nueva | |
| 20,1–21,8 | From modern glass doors | Puertas de vidrio (P6) | GLASS DOORS |
| 21,8–23,6 | To beautiful finishes | Nicho de hojas, grifo dorado, válvula cromada | FINISHES |
| 23,6–26,0 | (sin voz: no hay toma de esa frase) | Félix con la tablet mostrando diseños | NEW SHOWER CATALOG |
| 26,0–29,8 | Before even think remodel… just think about the shower | Félix → ducha de mármol (P1) | JUST THINK ABOUT THE SHOWER |
| 29,8–32,3 | We are West Home Improvement. Let's make it happen! | Félix con el camión | Píldora con el logo |
| 32,3–36,4 | | Ducha terminada (P2) | LET'S TRANSFORM YOUR SHOWER + logo |

## Sonido

- Efectos: **solo la librería del cliente** (`video/sfx-library`). Cada letra o palabra que aparece suena con un clic de
  teclado mecánico (11 variantes alternadas); las palabras clave llevan pop, golpe grave, flash, shutter, vidrio o chasquido.
- Música: instrumental original de 110 BPM (ElevenLabs Music v2.5 vía Higgsfield). Drop en el corte a la ducha vieja,
  *tape stop* en el freeze de 1990s, filtro que se abre hasta el drop del antes/después, salida empalmada al compás.
- Voz −14 LUFS en el máster; música bajo la voz con ducking.

## Rehacer

```bash
python3 video/sfx-library/build_library.py <sfx_drive> <trabajo>/sfxlib   # librería de SFX
python3 edit/extract_all.py                    # tramos 4K → intermedios
python3 edit/render.py out/seg0.mp4 --from 0 --to 9.1   # … en 4 partes
python3 edit/audio.py
```
`core.ROOT` apunta a la carpeta de trabajo de la sesión; las fuentes vienen de las carpetas de Drive del cliente.
