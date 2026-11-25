# Pipeline de montaje GEODA

- `builder.py`: montador genérico (planos 9:16, detección de caras, ubicación de textos, subtítulos, audio, exportación).
- `build_a10X*.py`: configuración de cada video ya producido (A1-01 v2, A1-02 v3, A1-03 v2, A1-04 v2, A1-05 v5 son los vigentes).
- `motion_v3.py` (A1-02) y `motion_a101_v2.py` (A1-01): hooks y gráficos animados sobre fotos reales (destellos, frasco tachado,
  X que cae, reloj 7→3, bacterias y nube de olor, revelación de la piedra), sin deformar la etiqueta.
- `tools/tts_multi.py`: todas las frases de un personaje en una sola petición de voz (misma voz exacta).
- `tools/pauses.py` + `tools/verify_lines.py` + `tools/cut_lines.py`: cortar por pausas reales, verificar cada frase con STT
  aislado y recortar pausas internas > 0,18 s.
- `tools/endcard_real.py`: tarjeta final con el producto real sobre un ambiente (baño).
- `tools/qa_sheet.py`: hoja de QA con las guías de zona segura del brief.
- `hf.sh`: subir archivos, enviar trabajos y descargar resultados de la API de Higgsfield (credencial vía proxy).
- `tts_gemini.py`: voz con Gemini TTS (notas de dirección + transcripción, para que no lea la instrucción).

Las rutas apuntan al directorio de trabajo temporal de la sesión; las reglas están en `../REGLAS_PRODUCCION.md`.
