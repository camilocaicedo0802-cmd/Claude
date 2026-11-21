# Hackeó GTA 6 desde la tele de un hotel — sello: REAL

Short vertical (1080×1920, 30 fps, ~57 s) hecho con Remotion, con personajes y fondos dibujados por código.

## Cuidados

- No se dice el nombre del chico ni se le dibuja parecido (era menor de edad): es un muñeco genérico con capucha.
- Sin logo de Rockstar, sin imágenes, música ni sonidos reales del juego o de apps: todo es dibujo y síntesis propios.
- Sin burlas de su salud: la puerta del hospital se cierra con sobriedad.
- La ironía con la policía va en el cartel («PROTECCIÓN POLICIAL» y «★★★★★ IDEAL PARA HACKEAR»); no aparece ningún agente.

## Voz

- Narrador: Gemini 2.5 Flash TTS, voz Charon. Voces extra: Puck y Leda (comentarios, con filtro de celular) y
  Enceladus (el mensaje del hacker: frío, casi susurrado y con eco).
- `scripts/voz_gemini.py` (narrador), `scripts/voces_extra.py`, `scripts/montar_voz.py` (inserta las voces, ajusta la
  escalada, el remate y las pausas), `scripts/alinear.py --tempo 1.11` y `scripts/efectos_voz.py`.
- Medido: 200 palabras/min; solo dos pausas (0,42 s antes de «los videos son reales» y 0,52 s antes de «Todo por…»;
  ningún otro silencio supera 0,07 s); escalada 6,7 → 7,5 → 8,9 sílabas/s; última frase 12 % más lenta; remate 2,3
  semitonos más grave.
- `alinear.py` vuelve a transcribir el audio final para fijar los tiempos de las palabras (evita el desfase acumulado).

## Imagen

- Subtítulos de 1–2 palabras, blancos con borde negro, a ~60 % de la altura; ocultos en los comentarios y la amenaza.
- Sin cortes secos: barridos o la cámara se mete en una pantalla (transición `pantalla` en `Toma.tsx`).
  Se comprobó cuadro a cuadro que no hay saltos aislados.
- Paleta: azul noche (hotel), neón morado y rosa (digital), ámbar → rojo (oficina), blanco frío y negro (final).
- Piezas en `src/componentes/Hacker.tsx` (tele con giro de 360° y vista en corte, el aparatito, túnel digital,
  edificio, oficina en alarma, reloj, puertas, billetes…).

## Sonido

- `scripts/synthwave.py`: música synthwave original y efectos (zumbido de tele, cierre de bolsa, puerta de auto, neón,
  notificación, bóveda, murmullo, tictac, chispas, servidores, caja registradora, puerta, nota sostenida, clic, glitch).
- Música a −17,5 dB bajo la voz (−15,2 dB después del giro); silencio total en el giro; se apaga en el remate.
- Máster a −14,1 LUFS, pico real −2,3 dBTP.

## Generar

```bash
npm ci
python3 scripts/sonidos.py --duracion-musica 10 && python3 scripts/synthwave.py --duracion 58
npx remotion render src/index.ts Completo out/completo.mp4
SOLO_AUDIO=1 npx remotion render src/index.ts Completo out/audio.wav --codec=wav
ffmpeg -i out/completo.mp4 -i out/audio.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le out/mux.mkv
bash scripts/masterizar.sh out/mux.mkv out/completo-final.mp4
```
