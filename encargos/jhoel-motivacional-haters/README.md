# Jhoel · Motivacional Texto · "Los haters"

Reel vertical (1080×1920, 30 fps, 12,4 s) que recrea el video de referencia con los B-rolls propios de Jhoel.

- **Texto** (igual a la referencia): "Los haters saben quién eres, pero tú no los conoces a ellos." → "Sabes por qué?" → "tú has hecho algo increíble y ellos no han hecho nada."
- **Tipografía**: TikTok Sans Bold, blanca con sombra suave (la del texto nativo de TikTok/IG que usa la referencia).
- **Música**: provisional, *akiaura, LONOWN, STM – Sleepwalker* (carpeta "Musica reals/motivacion"), con el drop en el corte de 5,33 s. El archivo de referencia no trae audio; hay que cambiarla por la canción original del ejemplo.

## Cortes

| Tiempo | Clip (Drive "Recursos/B rols") | Texto |
| --- | --- | --- |
| 0,00–1,83 | Deporte/gym superior/IMG_6502 (curl) | Los haters… |
| 1,83–3,82 | Deporte/gym superior/IMG_5956 (jalón) | Los haters… |
| 3,82–5,33 | Deporte/gym superior/IMG_8724 (silueta) | Sabes por qué? |
| 5,33–7,33 | life stile/santo paracaídas/IMG_5950 | tú has hecho… |
| 7,33–8,33 | Deporte/Correr/C0294 | tú has hecho… |
| 8,33–9,33 | life stile/avioneta/yo avioneta 2 | tú has hecho… |
| 9,33–10,33 | Deporte/Correr/correr atardecer 3ra persona | tú has hecho… |
| 10,33–11,32 | life stile/avioneta/despegue avioneta | tú has hecho… |
| 11,32–12,40 | Deporte/Correr/C0292 | tú has hecho… |

## Regenerar

`render.py` espera los clips descargados en `<dir>/clips/<nombre>.mov` y las fuentes en `<dir>/fonts/`:

```bash
python3 render.py <dir> <musica> <inicio_musica_s> salida.mp4 beat   # cortes al ritmo de la música provisional
python3 render.py <dir> <musica> <inicio_musica_s> salida.mp4 ref    # cortes exactos de la referencia (para la canción original)
```
