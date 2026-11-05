# Memoria del proyecto

## Videos de YouTube de Ali

Cuando Ali adjunte una locución (mp3) y un guion (PDF) para "el siguiente video", o pida algo sobre sus
documentales (partes en mp4, versión optimizada, miniaturas, descripción, créditos, cambiar la música),
usa la skill `editor-videos-youtube-ali` (`.claude/skills/editor-videos-youtube-ali/`). Recoge el proceso
completo y todas las correcciones de los episodios Laurel Hill, I-80 Wyoming, Cumberland Gap, Donner Pass
y Atlantic Avenue. El código de cada episodio está en `video/<episodio>/`.

Lo esencial:
- Responde en español, breve, con estado y tiempo estimado; envía los archivos en cuanto estén.
- Solo material apto para monetizar (PD, CC0, Unsplash, CC BY con atribución; nunca BY-SA, NC, ND).
- Música: pídele pistas de la Biblioteca de audio de YouTube Studio; si no llegan, música original
  sintetizada. No uses Kevin MacLeod ni películas de archivo (hubo un reclamo de copyright).
- Música y efectos bajos para no tapar al narrador; voz a −14 LUFS.
- Entrega: 4 partes mp4 + archivo único optimizado (H.264 1080p ≈350 MB), 2 miniaturas, descripción con
  capítulos y créditos completos (≤10.000 caracteres).
