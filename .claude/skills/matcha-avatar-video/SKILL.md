---
name: matcha-avatar-video
description: Crea videos UGC con avatares de IA para promocionar el Té Matcha Grado Ceremonial de LO Laboratorios Outlet en Higgsfield — el avatar "doctor" que habla a cámara en español con acento colombiano (Veo 3.1 Lite), las tomas de producto y estilo de vida (Kling 3.0) y la variante de creadora UGC en cocina (storyboard de 8 tomas). Usar cuando pidan videos, anuncios, reels o UGC del té matcha, nuevas escenas o guiones con el doctor o la creadora, o repetir la campaña de matcha con otros textos.
---

# Videos con avatar — Té Matcha (Higgsfield)

Esta skill guarda la configuración que funcionó en Higgsfield para la campaña del **Té Matcha Grado Ceremonial Premium de LO Laboratorios Outlet**. Todo se genera con las herramientas MCP de Higgsfield (`generate_image`, `generate_video`, `generate_*_batch`, `jobs_wait`, `show_generation_by_ids`). No uses otras plataformas para esta campaña.

Los valores exactos (modelos, IDs, parámetros) están en `config.json`. Los prompts completos, listos para copiar, están en `reference/`.

## Antes de generar

1. **Créditos.** Cada imagen y cada video gasta créditos de la cuenta de Higgsfield. Antes de lanzar un lote, consulta el costo con `get_cost: true` y confírmalo con el usuario. No pases `use_unlim` salvo que el usuario lo pida.
2. **Referencias.** Reutiliza los IDs guardados en `config.json` en `medias[].value`; no hace falta volver a subir nada:
   - Producto (lata de matcha): `850cf9d2-5981-41bd-8b88-6c127eac798f` (`media_input`).
   - Avatar doctor: `b7b169c4-79ba-429c-b7da-d2e8019c5b66` (job de imagen).
   - Avatar creadora: `c3eef1aa-e355-4d37-87a0-f865097cfe86` (job de imagen).
   Si un ID ya no existe (cuenta distinta o borrado), sube la imagen equivalente de `assets/` con `media_upload` → PUT → `media_confirm` y usa el nuevo `media_id`.
3. **Formato.** Todo es vertical **9:16** (Reels, TikTok, Shorts).

## Flujo A — Doctor que habla a cámara (formato principal)

Anuncio de ~48 s armado con 6 clips de 8 s. Cada clip sale de un fotograma fijo del doctor y luego se anima con voz.

**Paso 1 — Fotograma de cada escena** (`generate_image` o `generate_image_batch`):
- `model: "nano_banana_2_1"`, `aspect_ratio: "9:16"`, `resolution: "2k"`, `thinking_level: "medium"`.
- `medias`: avatar doctor con `role: "image"`; si la lata sale en la escena, agrega también el producto con `role: "image"` (siempre en ese orden: 1 = doctor, 2 = lata).
- Prompt: el de la escena en `reference/doctor-ugc.md`.

**Paso 2 — Animar con voz** (`generate_video` o `generate_video_batch`):
- `model: "veo3_1_lite"`, `aspect_ratio: "9:16"`, `duration: 8`, `generate_audio: true` (en este modelo viene apagado por defecto, así que hay que pasarlo explícitamente).
- `medias`: el fotograma del paso 1 con `role: "start_image"`.
- Prompt: el de la escena en `reference/doctor-ugc.md`.

**Estructura del guion (orden de montaje):**

| # | Escena | Frase |
|---|---|---|
| 1 | Gancho: pasillo de la clínica, selfie caminando | "¿Vas por tu tercer café del día... y sigues sintiéndote apagado? Espera, esto te interesa." |
| 2 | Problema: escritorio, café de papel | "A las tres de la tarde llega el bajón, y casi todos hacemos lo mismo: otro café." |
| 3 | Revelación: lata junto a la cara | "Por eso cada vez más personas lo están cambiando por esto: té matcha grado ceremonial." |
| 4 | Por qué: explica contando con los dedos | "Tiene cafeína natural, pero con L-teanina, un aminoácido estudiado por su relación con la calma y el enfoque." |
| 5 | Beneficio: toma un sorbo de matcha latte | "Muchos lo sienten como energía más estable, sin aceleres. Y se prepara en un minuto." |
| 6 | Llamado a la acción: señala la lata y luego hacia abajo | "Si tu tarde depende de otro café, haz el cambio. Toca el enlace y descúbrelo." |

Cada frase debe caber en 8 s (unas 20 palabras como máximo). Para escribir guiones nuevos, mantén los 6 tiempos y cambia solo las frases.

## Flujo B — Tomas de apoyo (b-roll) con Kling

Planos sin diálogo para intercalar entre los clips del doctor.

**Paso 1 — Fotograma:** `nano_banana_2_1`, 9:16, `2k`, `thinking_level: "medium"`. En `medias` va el producto con `role: "image"` cuando la lata aparece.
**Paso 2 — Video:** `model: "kling3_0"`, `aspect_ratio: "9:16"`, `duration: 5`, `mode: "std"`, `sound: "off"`, con el fotograma como `start_image`.

Las 5 tomas (oficinista cansada, hero de producto, batido macro, vertido sobre leche con hielo, mujer tomando matcha en la oficina) están en `reference/broll-kling.md`.

## Flujo C — Creadora UGC en cocina (storyboard de 8 tomas)

Variante con una creadora joven que prepara el matcha en su cocina. Se planifica como tableros de 8 viñetas (21:9) que equivalen a un clip de 15 s cada uno:
1. Tablero: `model: "gpt_image_2"`, `aspect_ratio: "21:9"`, `resolution: "2k"`, `quality: "high"`; `medias` = producto, avatar creadora y (para el tablero 2 en adelante) el tablero anterior, todos con `role: "image"`.
2. Pase de realismo: `model: "seedream_v5_pro"`, `aspect_ratio: "21:9"`, `resolution: "2k"`, con el tablero como referencia.

Prompts en `reference/creadora-storyboard.md`. En la campaña original este flujo llegó hasta los tableros; si el usuario quiere el video, confirma con él el modelo de animación antes de gastar créditos.

## Reglas que se mantienen siempre

- **Producto fiel.** Una sola lata por toma, a tamaño real (~13 cm), con la etiqueta de frente y sin redibujar el texto: etiqueta crema, "TÉ MATCHA" en verde oscuro, línea dorada "GRADO CEREMONIAL PREMIUM", logo de LO Laboratorios Outlet arriba y una franja verde abajo.
- **Avatar consistente.** El doctor tiene unos 42 años, piel trigueña clara, cabello oscuro con canas en las sienes, barba corta, gafas rectangulares, bata blanca sin texto, camisa azul claro y fonendoscopio negro, en un consultorio luminoso en Bogotá. Repite "the exact same man from the reference photo" y esa descripción en cada fotograma.
- **Voz.** "Latin American Spanish with a warm, natural Colombian accent". Solo la voz y el ambiente: sin música, sin subtítulos y sin texto en pantalla. La música y los subtítulos se agregan en edición.
- **Estética UGC.** Grabado con celular, luz de ventana, piel real con poros. Sin filtros de belleza, sin logos extra y sin placas con el nombre.
- **Afirmaciones prudentes.** No inventes beneficios de salud. Usa formulaciones como "estudiado por su relación con", "muchos lo sienten". El avatar es un médico generado con IA: avísale al usuario que revise las normas de publicidad de su país (en Colombia, INVIMA) y de cada plataforma sobre contenido sintético y respaldo de profesionales de la salud antes de pautar.

## Entrega

Lanza las escenas independientes con `generate_video_batch`, espera con `jobs_wait` y muestra el lote con un único `show_generation_by_ids`. Entrega los IDs y URLs en el orden de montaje de la tabla.
