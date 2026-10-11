# Ejemplo resuelto: editorial monocromo de motion graphics

Caso real hecho con esta skill. **No es un estilo por defecto**: sirve para ver el nivel de detalle esperado en cada fase.

- **Referencia:** vídeo de 8.5 s (576×1024) con locución motivacional. Fondo papel `#E4E4E4`, recortes en B/N con sombra, círculo discontinuo, trazo de pincel en S, caligráfica + palo seco negro, empuje, oscurecimiento con transformación e iris; piano a −40 dB y whooshes en cada objeto. Hoja de contactos: `referencia_2fps.jpg`.
- **Encargo:** locución de 41 s sobre «el tiempo vale más que el dinero; el móvil te roba la atención», con la misma música y SFX en cada elemento destacado.
- **Resultado:** 42.6 s, 1080×1920, 30 fps, −14.4 LUFS. Hoja de contactos: `resultado_2fps.jpg`.
- `estilo_ejemplo.md`: el estilo.md completo, con la corrección aprobada al final.
- `src/`: escenas y componentes tal como se entregaron. `TextBlock.tsx` es la versión inicial de `captions/EditorialBlock.tsx`.

## Storyboard usado
| Escena | Tiempo | Fondo | Objeto (≙ referencia) | Palabras clave | Transición |
|---|---|---|---|---|---|
| E1 | 0–5.9 | papel | reloj de arena en círculo → trazo → monedas (≙ bombilla → STOP) | todos los días / más valioso / dinero | sale con empuje |
| E2 | 5.7–10.4 | papel + banda | tarjeta tachada que cae → móvil que sube (≙ estatua con banda) | cuenta bancaria / bolsillo | zoom dentro de la pantalla |
| E3 | 10.3–16.1 | negro | móvil: notificaciones, rejilla de vídeos, feed deslizándose | notificación / video / deslizas la pantalla | iris a papel |
| E4 | 15.8–20.1 | papel | reloj de bolsillo que se desintegra en partículas | entregando / recuperar | golpe a negro |
| E5 | 20.0–21.2 | negro | reloj de frente con corona de marcas (zoom de impacto) | tiempo | empuje |
| E6–8 | 20.9–34.0 | papel → negro | señal de peligro → busto con censura → silueta + móvil que absorbe el cerebro (≙ estatua → cerebro) | peligroso / te das cuenta / consumes contenido / tu atención | iris |
| E9–10 | 33.8–38.8 | papel | cerebro en círculo → monedas con flecha que vuelve | esto / puede volver | oscurecimiento |
| E11 | 38.6–41.5 | negro | reloj de arena con hilo de arena | jamás | iris gris |
| Cierre | 41.3–42.6 | gris `#B6B6B6` | @usuario → negro | — | — |

## Lecciones (ya incorporadas a la skill)
- Whisper llegaba 0.1–0.3 s tarde tras las pausas; `transcribe.py` lo corrige.
- La máscara del barrido recortaba los descendentes de la caligráfica; `EditorialBlock` lleva padding y quita la máscara al terminar.
- Los trazos cruzaban textos y el poste de una señal asomaba en otra escena; se resolvió revisando fotogramas sueltos antes del render.
- La suma de voz y SFX daba un pico de +0.2 dBFS; `finalize.sh` aplica el limitador.
