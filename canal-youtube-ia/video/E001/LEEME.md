# E001 · Producción del video "Le hicieron un funeral de Estado a una pierna"

Estado al 29-oct-2026: guion terminado (`guiones/E001-pierna-santa-anna.md`), guion de planos del piloto con sus prompts (`guiones/E001-piloto-prompts-nano-banana.md`, `video/E001/planos_piloto.json`) y **montaje automático listo** (`scripts/e001_montaje.py`). Ya hay una animática del piloto (93,6 s) con marcadores en lugar de imágenes y sin voz. Faltan la voz y las imágenes, y las dos esperan una decisión de pago del usuario (ver abajo).

## Decisiones del usuario

- **Voz:** ElevenLabs. Narrador cercano, como "un amigo que cuenta historias"; voz natural y fluida.
- **Imágenes:** Nano Banana (Gemini) o Google Flow, en estilo stickman.
- **Edición:** movimiento, textos grandes, fechas, mapas y sellos los añade Claude por código; las imágenes no llevan texto.
- **Alcance:** primero un piloto de unos 90 segundos (bloques 1 a 3) para aprobar estilo, voz y ritmo; después, el video completo.

## Claves necesarias (secretos del entorno; nunca en el chat ni en el repositorio)

| Variable | Para qué |
|---|---|
| `ELEVENLABS_API_KEY` | Narración con marcas de tiempo para sincronizar imágenes y textos |
| `GEMINI_API_KEY` | Imágenes con Nano Banana por API (solo si no se generan a mano en Flow) |
| `OPENAI_API_KEY` | Alternativa: voz con `gpt-4o-mini-tts` (tiempos por palabra con transcripción) e imágenes con `gpt-image` |

Se añaden en el menú del entorno → Editar, y se cargan en una sesión nueva. `.env.local` está en `.gitignore`.

**30-oct-2026:** el usuario va a añadir `OPENAI_API_KEY` y a cambiar `GEMINI_API_KEY` por la de otra cuenta de Google. Al abrir la sesión nueva: listar los modelos de cada clave, comprobar que ambas tienen saldo (ni OpenAI ni los modelos de imagen de Gemini tienen nivel gratuito), comparar la voz de OpenAI con las 4 voces de ElevenLabs y añadir a `e001_voz.py` y `e001_imagenes.py` la opción de usar OpenAI. Si la nueva clave de Gemini tiene facturación, las imágenes siguen con Nano Banana: OpenAI avisa que `gpt-image` puede fallar al mantener un personaje recurrente.

## Verificación del 29-oct-2026

**ElevenLabs.** La clave funciona, pero la cuenta está en el **plan gratuito**:

- Quedan **1.672 de 10.000 caracteres** hasta el 10-nov-2026. La parte 01 (piloto) usa 1.140; el video completo, 12.272.
- La API responde `402 paid_plan_required` con las voces de la biblioteca: *"Free users cannot use library voices via the API"*. Solo se podrían usar por API las voces prediseñadas, que no tienen acento latinoamericano.
- El plan gratuito **no da licencia comercial** y exige atribuir a ElevenLabs. Para un canal monetizado hace falta al menos **Starter** (6 USD al mes; 1 USD el primer mes según la página de precios; 30.000 caracteres al mes).
- La cuenta ya tiene 7 voces latinoamericanas añadidas desde la biblioteca. Candidatas para el narrador:

| Clave en `e001_voz.py` | Voz | Descripción de ElevenLabs |
|---|---|---|
| `lujan` (recomendada) | Luján - Warm, Natural, Neutral | Cálida, natural, acento colombiano neutro, para narración |
| `rodrigo` | Rodrigo Zabú - Latin Spanish | Cálida, conversacional; locutor con experiencia en documental |
| `albert` | Albert - Deep, Resonate and Compelling | Grave y resonante, de audiolibro |
| `cesar` | Cesar - Slow, Meditative, Warm | Lenta y meditativa |

**Gemini.** La clave funciona, pero el proyecto **no tiene facturación activa**: los modelos de imagen responden `429` con `generate_content_free_tier_requests, limit: 0`, y ninguno tiene nivel gratuito. Modelos disponibles para la clave y tarifa por imagen en 2K:

| Modelo | Nombre comercial | USD por imagen 2K |
|---|---|---|
| `gemini-3.1-flash-image` (el que usa `e001_imagenes.py`) | Nano Banana 2 | 0,101 |
| `gemini-3-pro-image` | Nano Banana Pro | 0,134 |
| `gemini-nano-banana-2.1` | Nano Banana 2.1 | 0,0504 |
| `gemini-2.5-flash-image` | Nano Banana (retirada prevista el 15-mar-2027) | 0,039 (1K) |

El piloto lleva 24 imágenes (REF y 23 planos; S12 es un mapa por código): unos **2,40 USD** con Nano Banana 2, más los reintentos.

## Scripts

| Script | Qué hace |
|---|---|
| `scripts/e001_voz.py` | `generar --voz lujan`: narración por API con tiempos por carácter. `alinear`: tiempos de un MP3 hecho a mano en la web. `cuota`: caracteres que quedan |
| `scripts/e001_imagenes.py` | Genera `REF` y luego los planos que falten en `video/E001/img/`, adjuntando `REF` donde el plano lo pide |
| `scripts/e001_montaje.py` | Montaje completo: movimiento de cámara, rótulos (Anton, Fraunces, Inter), mapa de Natural Earth, sellos, efectos de sonido sintetizados y normalización a -14 LUFS. Sale en `trabajo/E001/piloto.mp4` y `piloto.srt` |

El montaje funciona con lo que haya: sin narración estima los tiempos y quema subtítulos (animática); sin una imagen, pone un marcador "imagen pendiente". Los textos en pantalla, su posición y los efectos de cada plano están en `EDICION`, dentro del script. Fuentes y mapas se descargan solos a `trabajo/` (no se versiona).

## Pasos siguientes

1. **Voz.** El usuario elige una de las 4 voces y uno de estos caminos:
   - **Recomendado:** pasar ElevenLabs a Starter y ejecutar `python3 scripts/e001_voz.py generar --voz <clave>`.
   - Gratis (sin uso comercial): generar a mano la parte 01 de `guiones/E001-textos-elevenlabs.md` en la web con la voz elegida y la configuración recomendada, subirla como `video/E001/audio/E001_01.mp3` y ejecutar `python3 scripts/e001_voz.py alinear`.
2. **Imágenes.** Uno de estos caminos:
   - Activar la facturación del proyecto de Gemini y ejecutar `python3 scripts/e001_imagenes.py REF`; revisar `REF.png` y luego `python3 scripts/e001_imagenes.py` para el resto.
   - A mano en Flow: subir los PNG a `video/E001/img/` con el código del plano.
3. Con las imágenes, ajustar en `EDICION` el `foco` de la cámara y la posición de los textos según dónde quede el espacio libre de cada imagen.
4. `python3 scripts/e001_montaje.py` y entregar el piloto. Opcional: música de la Biblioteca de Audio de YouTube en `video/E001/audio/musica.mp3` (se baja sola bajo la voz).
5. Recoger comentarios y producir el resto del video.
6. Antes del video completo, verificar los 23 datos marcados en `guiones/E001-pierna-santa-anna.md`.
