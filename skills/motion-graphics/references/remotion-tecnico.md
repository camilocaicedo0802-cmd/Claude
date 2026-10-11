# Remotion: patrones y problemas resueltos

Problemas ya encontrados y su solución, más los patrones de la plantilla. Las skills oficiales de Remotion (`<proyecto>/.claude/skills/remotion-best-practices`) son la referencia de la API; aquí está lo específico de este flujo.

## Estructura del proyecto

```
src/
  index.ts         registerRoot
  Root.tsx         <Composition id="Main"> + carpeta "Escenas" con cada escena registrada aparte
  theme.ts         W, H, FPS, DURATION_S y tokens (C, F, CAPTION_LOOKS)
  fonts.ts         loadFont de cada fuente en public/fonts
  Main.tsx         una <Sequence> por escena + voz + música + SFX + capas globales (grano, viñeta)
  data/captions.ts salida de transcribe.py (Caption[] con índice comentado)
  data/sfx.ts      mapa de SFX {t, file, vol, note}
  scenes/          una escena por archivo: export const S0X = {start, end}; componente con prop start
  components/      Camera, Cutout, Transitions, Overlays, BrushPath, DashedCircle, Phone, Props, Dissolve
  captions/        EditorialBlock, WordPop, KaraokePage (+ util, types)
  media/ARoll.tsx  metraje con golpes de zoom
  lib/             anim.ts (kf, kfs, kcolor, springy, curvas), useSceneTime.ts
```

## Tiempo

- Las escenas trabajan con **tiempo global en segundos** (`g = start + frame/fps`), así los índices de `captions.ts` (que están en ms globales) cuadran sin conversiones. `useSceneTime(start)` devuelve `{t, g}`.
- Registra cada escena con su `{start, end}` exportado y úsalo en `Main.tsx` (`from={Math.round(S.start*fps)}`). Las escenas se solapan exactamente lo que dura la transición.
- Pon los cambios de escena en las pausas de la voz. Las palabras clave de una escena deben caer dentro de su rango.
- `useVideoConfig().durationInFrames` dentro de una `<Sequence>` no sirve para saber cuándo acaba la secuencia: pasa la duración como prop (`Push` tiene `seqDur`).

## Animación

- Todo con `useCurrentFrame()` e `interpolate()`. CSS `transition` y `animation` no se renderizan.
- `kf(t, [t0,t1], [a,b], easing)` es la interpolación con límites; `kfs` acepta varias claves; `springy(t, start, dur, overshoot)` da un muelle simple (0→1).
- Usa `scale`, `translate` y `rotate` como propiedades CSS separadas. `transform` solo en la cámara, donde hace falta el orden translate→scale→rotate→translate.
- La cámara es un `div` de tamaño del cuadro con `transform: translate(W/2,H/2) scale(s) rotate(r) translate(-cx,-cy)`: coloca el punto del mundo (cx, cy) en el centro. Los objetos se posicionan en coordenadas del mundo, que pueden pasar de 1920 en vertical para un mundo alto.
- Para pasar de coordenadas del mundo a pantalla (por ejemplo, para animar algo de la pantalla hacia un objeto del mundo): `sx = W/2 + (x - cx)*scale`, `sy = H/2 + (y - cy)*scale`.

## Texto

- **Fuentes:** con `loadFont` de `@remotion/fonts` desde `public/fonts`. `fonts.ts` se importa en `Root.tsx`. Sin esto, algunos fotogramas salen con la fuente de sistema.
- **Máscaras y desenfoque:** una `mask-image` o un `filter` sobre un `span` recortan lo que sobresale de su caja, como los descendentes de la caligráfica. Pon `padding` y el `margin` negativo equivalente (`EditorialBlock` lo hace) y quita la máscara cuando la animación termina.
- **Aberración cromática** barata: `text-shadow: -1px 0 rgba(0,170,255,.22), 1px 0 rgba(255,110,30,.22)`.
- **Contorno tipo TikTok:** `-webkit-text-stroke: 10px #000; paint-order: stroke fill` (mira `lookStyle`).
- **Medidas:** el ancho de una palabra en px es aproximadamente `n_letras × tamaño × 0.55–0.62` para palo seco bold y `× 0.40–0.45` para caligráfica. Comprueba con fotogramas sueltos que nada se sale del margen (≥ 80 px a los lados).
- La puntuación se limpia por defecto (`cleanWord`). Las minúsculas son opcionales y dependen de la referencia.

## Imágenes y efectos

- `Img` de `remotion` (espera a que cargue). Sombra con `filter: drop-shadow(...)`. El brillo para siluetas, con `filter: brightness(0.07)`.
- **Disolución en partículas:** `DissolveCutout` (máscara SVG con `feTurbulence` y umbral animado) + `Particles`.
- **Desenfoque de movimiento direccional:** filtro SVG `<feGaussianBlur stdDeviation="X 0">` referenciado con `filter: url(#id)` (`Push`). `HtmlInCanvas` y `@remotion/motion-blur` necesitan Chrome 149+ con flag: evítalos salvo que el entorno lo permita.
- **Iris o barridos con borde suave:** `mask-image: radial-gradient(...)` o `linear-gradient(...)`.
- **Grano:** 8 texturas PNG (de `make_grain.py`) rotando cada frame con desplazamiento aleatorio, `mix-blend-mode: overlay`. Es barato y determinista.

## Audio

- `<Audio>` de `@remotion/media` admite `from`, `volume` (número o función de frame), `trimBefore`, `loop` y `premountFor`.
- Los SFX se mapean desde `data/sfx.ts` (bucle intencionado: se controlan como un conjunto).
- Remotion suma las pistas sin limitador, así que el pico puede pasar de 0 dBFS. Usa siempre `finalize.sh`: ajusta la sonoridad y aplica un limitador sin recodificar el vídeo.

## Render y revisión

- `scripts/stills.mjs` empaqueta una vez y renderiza los segundos que le pases a media resolución. Úsalo en bucle de revisión (montar hoja de contactos con PIL y mirarla) antes del render completo.
- Render completo: `npx remotion render Main out/v1.mp4 --concurrency=4 --crf=18`. Unos 4 min para 40 s a 1080×1920 con 4 núcleos. Los filtros SVG y los `drop-shadow` grandes son lo más caro.
- Si `npx remotion render` no encuentra navegador, descarga chrome-headless-shell; si la red lo bloquea, usa `--browser-executable` con un Chromium local.
- En entornos sin GUI, `npx remotion studio` no sirve para que el usuario vea el resultado: entrega renders y fotogramas.

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| «pantalla» se lee «rantalla», «jamás» se lee «¡amás» | máscara que recorta descendentes | padding y margen negativo; quitar la máscara al terminar |
| un trazo pasa por encima del texto | ruta del `BrushPath` mal trazada | volver a trazar la ruta por fuera de las cajas de texto (comprobar con fotogramas sueltos) |
| aparece un objeto de otra escena en el borde (poste, banda…) | el mundo es continuo y la cámara lo encuadra | acortar el objeto o moverlo fuera del encuadre |
| la transición termina antes o después de tiempo | `durationInFrames` del contexto | pasar `seqDur` en segundos |
| la primera palabra tras una pausa llega tarde | retraso de Whisper | `transcribe.py` ya ancla al inicio real de la voz |
| el render tiene clipping | suma de voz y SFX | `finalize.sh` (limitador a −1.4 dBFS) |
