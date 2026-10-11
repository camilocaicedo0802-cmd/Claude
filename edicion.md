# edicion.md — Montaje de la camiseta Ryan Castro "El Cantante del Ghetto"

Salida: `out/camiseta_bombastik.mp4` — 1080×1920, 30 fps, 21,33 s, H.264 CRF 16, AAC, -14,1 LUFS.
Render: `REMOTION_BROWSER=<ruta a headless_shell> npx remotion render src/index.ts CamisetaBombastik out/camiseta_bombastik.mp4`

## Música
- BOMBASTIK (Ryan Castro, Blaiz Fayah, Tribal Kush), **90 BPM** (1 pulso = 20 fotogramas, 1 compás = 2,67 s).
- Tramo: **1:07,245 → 1:28,57** (compases 25–32): el estribillo "Beki beki… loba, loba bombastik".
  Arranca justo en el drop; cada mitad de 4 compases termina en "loba, loba bombastik" → cierre natural.
- Ganancia -2,7 dB (→ -14 LUFS como la referencia), entrada de 80 ms, salida en corte seco.
- Audio de las tomas silenciado (solo conversación de fondo; Whisper en `analisis/whisper_IMG_*.json`).

## Tomas usadas (6 de 10) y descartes
| # | Timeline | Toma (seg.) | Diseño | Plano |
|---|---|---|---|---|
| 1 | 0,00–2,67 | IMG_6016 (1,0) | Espalda | General girado + acercamiento rápido final |
| 2 | 2,67–5,90 | IMG_6017 (0,6) | Espalda | Macro grafiti + retrato, paneo |
| 3 | 5,90–8,00 | IMG_6019 (1,0) | Espalda | Macro cara |
| 4 | 8,00–10,67 | IMG_6024 (5,2) | Delantero | Logo de cerca, crece (en "loba bombastik") |
| 5 | 10,67–13,33 | IMG_6018 (2,4) | Espalda | Macro "CASTRO" → retrato → grafiti |
| 6 | 13,33–14,67 | IMG_6019 (7,3) | Espalda | Macro cara, otro encuadre (jump cut) |
| 7 | 14,67–17,90 | IMG_6022 (6,87) | Espalda | General recto, casi fijo |
| 8 | 17,90–21,33 | IMG_6023 (4,0) | Delantero | General con etiqueta, girando (cierre en "loba bombastik") |

Espalda **15,3 s (72 %)** · Delantero **6,0 s (28 %)** (referencia: 68 / 32).
Descartadas: IMG_6015 y IMG_6021 (generales casi iguales a 6016/6022, se eligió la de movimiento más parecido a la referencia), IMG_6020 (dominante verde), y los tramos de 6017/6024 donde la cámara sale del estampado (desenfoque, tela vacía).

## Cortes y ritmo
Cortes secos en los fotogramas 80, 177, 240, 320, 400, 440, 537 → todos en pulso del tema; los de 177 y 537 adelantados 3 fotogramas al acento real del dembow (medido), como hace la referencia. Duraciones alternas largo/corto: 2,7 · 3,2 · 2,1 · 2,7 · 2,7 · 1,3 · 3,2 · 3,4 s.

## Color (por plano, `analisis/etalonaje.py` → `src/grades.ts`)
LUT por canal aplicada con filtro SVG en Remotion, 4 anclas medidas en cada plano:
tela negra → gris neutro (~#0B0B0B; delantero algo más alto para ver la prenda), pliegues → gris neutro,
**rojo del estampado → #DC363C** (igual en espalda y delantero), **blanco del texto → #D0D0CC** (el plateado de la referencia), altas luces topadas a 226.
Sin subtítulos, sin rótulos, sin marca de agua, sin transiciones (según lo acordado).
