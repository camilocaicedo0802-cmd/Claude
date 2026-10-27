# Jhoel · Motivacional Texto · "El tiempo es lo que menos sobra"

Reel vertical (1080×1920, 30 fps, 9,2 s) que recrea la segunda referencia: un solo plano de Jhoel manejando, visto desde el asiento del copiloto, con el texto fijo arriba.

- **Clip**: Drive "Recursos/B rols/auto/IMG_6925.mov" (BMW, 6,1 s a 60 fps) estirado a 9,2 s (0,66x) para durar lo mismo que la referencia.
- **Texto** (igual a la referencia, mismas líneas y posición): "El tiempo es lo que menos sobra / Tienes que jubilarte a los 30 / para ver a tus hijos crecer".
- **Tipografía**: Sofia Sans Condensed Medium (500), blanca con sombra suave. Es la alternativa libre más parecida a la condensada de la referencia (probablemente la fuente propia de Instagram, que no es de uso libre).
- **Color**: más oscuro, frío y algo desaturado para acercarse al clima nocturno de la referencia, con un degradado oscuro arriba para que el texto se lea sobre el techo claro del auto.
- **Música**: provisional, *I accept who I am – overc00ked (Slowed + Reverb)* (carpeta "Musica reals/motivacion") desde 5,2 s. El archivo de referencia no trae audio; hay que cambiarla por la canción original del ejemplo.

## Regenerar

`render.py` espera el clip en `<dir>/clips/drive_6925.mov` y la fuente en `<dir>/fonts/SofiaSansCond-500.ttf`:

```bash
python3 render.py <dir> <musica> <inicio_musica_s> salida.mp4
```
