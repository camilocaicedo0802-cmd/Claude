# Jhoel · Motivacional Texto · "El tiempo es lo que menos sobra"

Reel vertical (1080×1920, 30 fps, 9,25 s: lo que dura la música) que recrea la segunda referencia: un solo plano de Jhoel manejando, visto desde el asiento del copiloto, con el texto fijo arriba.

- **Clip**: Drive "Recursos/B rols/auto/IMG_6925.mov" (BMW, 6,1 s a 60 fps) estirado a 9,25 s (0,66x) para durar lo mismo que la música.
- **Alternativa** (`Jhoel_motivacional_tiempo_alternativa.mp4`): "auto/IMG_6924 (1).mov", los primeros 4,6 s a media velocidad y un poco más oscura que la principal. Arranca con Jhoel al volante, pasa a sus manos en el volante del BMW y termina en el camino por el parabrisas.
- **Texto** (igual a la referencia, mismas líneas y posición): "El tiempo es lo que menos sobra / Tienes que jubilarte a los 30 / para ver a tus hijos crecer".
- **Tipografía**: Sofia Sans Condensed Medium (500), blanca con sombra suave. Es la alternativa libre más parecida a la condensada de la referencia (probablemente la fuente propia de Instagram, que no es de uso libre).
- **Color**: oscuro (medios y altas luces bajos), frío y algo desaturado para acercarse al clima nocturno de la referencia, con un degradado oscuro arriba para que el texto se lea sobre el techo claro del auto.
- **Música**: `musica.mp3`, el audio original del reel de referencia, sin cambios (sin fundidos ni ajuste de volumen).

## Regenerar

`render.py` espera el clip en `<dir>/clips/drive_6925.mov` y la fuente en `<dir>/fonts/SofiaSansCond-500.ttf`:

```bash
python3 render.py <dir> musica.mp3 salida.mp4                            # IMG_6925
python3 render.py <dir> musica.mp3 alternativa.mp4 auto_6924 0 4.62 1    # IMG_6924, más oscura
```
