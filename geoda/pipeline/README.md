# Pipeline de montaje GEODA

- `builder.py`: montador genérico (planos 9:16, detección de caras, ubicación de textos, subtítulos, audio, exportación).
- `build_a102*.py`, `build_a101.py`, `build_a103.py`: configuración de cada video ya producido.
- `hf.sh`: subir archivos, enviar trabajos y descargar resultados de la API de Higgsfield (credencial vía proxy).
- `tts_gemini.py`: voz con Gemini TTS (notas de dirección + transcripción, para que no lea la instrucción).

Las rutas apuntan al directorio de trabajo temporal de la sesión; las reglas están en `../REGLAS_PRODUCCION.md`.
