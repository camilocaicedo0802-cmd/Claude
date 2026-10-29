# E001 · Producción del video "Le hicieron un funeral de Estado a una pierna"

Estado al 29-oct-2026: guion terminado (`guiones/E001-pierna-santa-anna.md`) y guion de planos del piloto con sus prompts (`guiones/E001-piloto-prompts-nano-banana.md`, `video/E001/planos_piloto.json`). Faltan la voz, las imágenes y el montaje.

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

Se añaden en el menú del entorno → Editar, y se cargan en una sesión nueva. `.env.local` está en `.gitignore`.

## Pasos en la sesión nueva

1. `npx -y @elevenlabs/cli@latest onboard check` para verificar la clave de ElevenLabs.
2. Proponer 3 o 4 voces en español latino de la biblioteca de ElevenLabs para que el usuario elija.
3. Generar la narración del piloto (bloques 1 a 3 de `guiones/E001-pierna-santa-anna-narracion.txt`) con marcas de tiempo por carácter.
4. Imágenes:
   - Por API: generar primero `REF` (hoja de personaje de Santa Anna) y usarla como referencia en los planos marcados. Confirmar antes el nombre y la tarifa vigente del modelo de imagen de Gemini.
   - A mano en Flow: el usuario sube los PNG a `video/E001/img/` con el código del plano.
5. Montaje: movimiento sobre cada imagen, textos con Anton, Fraunces e Inter, mapa por código (Natural Earth, dominio público), sellos del veredicto y efectos de sonido. Render en 1920×1080 a 30 fps.
6. Entregar el piloto, recoger comentarios y producir el resto del video.
7. Antes del video completo, verificar los 23 datos marcados en `guiones/E001-pierna-santa-anna.md`.
