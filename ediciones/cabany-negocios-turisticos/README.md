# Reel Cabany · "Haz crecer tu negocio turístico"

Video vertical en modo tutorial (1080×1920, 30 fps, 62 s) para agencias de viajes, tour operadores, guías y transportistas. Explica cómo registrarse en "Ofrecer mis servicios" de cabanypanama.com, con voz masculina de Google AI.

- `cabany_negocios_turisticos.mp4`: video final (H.264 + AAC 48 kHz, −14 LUFS).
- `portada.jpg`: cuadro de muestra.
- `guion/guion.txt`: texto narrado.
- `guion/voz_gemini_puck.wav`: voz sola, ya editada.
- `fotos_cliente/`: las 6 imágenes oficiales del cliente (pasos 1–6).
- `fotos_stock/`: fotos de Unsplash (licencia Unsplash: uso comercial gratuito, sin atribución obligatoria).
  - `agencia.jpg`: foto de Global Residence Index.
  - `tour.jpg`: foto de 雙 film.
  - `guia.jpg`: foto de Alain Gehri.
  - `transporte.jpg`: foto de Martin Kallur.
  - `montana.jpg`: foto de Kevin Charit.
- `proyecto/work/`: código que genera el video.

## Voz

- **Modelo:** Google Gemini TTS (`gemini-3.8-flash-tts`), voz masculina **Puck**, en español latino.
- **Indicación de estilo:** locutor con energía, confianza y calidez. Pronuncia "Cabany" como "Kabáni", "RUC" como "ruc" y "ATP" como "a te pe".
- **Edición:** se acortaron los silencios de más de 0.3 s y se aceleró un 8 % sin cambiar el tono. La duración bajó de 77 s a 60 s.
- **Alternativa:** también se generó la voz masculina **Achird**, más pausada.

## Estructura

| Tiempo | Voz | Pantalla |
| --- | --- | --- |
| 0:00 | ¿Tienes una agencia de viajes? ¿Eres tour operador, guía turístico o tienes transporte? | Cuatro cortes rápidos con foto a pantalla completa (agencia, tour, guía, van) e ícono de cada tipo |
| 0:06 | ¡Haz crecer tu negocio turístico con Cabany Panamá! | Montaña, texto y logo |
| 0:09 | Forma parte de nuestra plataforma y llega a más viajeros | Notificaciones de "¡Nueva reserva!" (tour, traslado, sendero) |
| 0:12 | ¿Cómo funciona? Seis pasos | Círculos 1–6 |
| 0:15 | **Paso 1:** regístrate gratis | Navegador: se escribe la URL, clic en "Ofrecer mis servicios" y formulario "Crea tu cuenta" que se llena solo |
| 0:21 | **Paso 2:** selecciona tu negocio | Panel "Ofrecer mis servicios", pestaña Tipo: se resalta cada tipo al nombrarlo y se marcan Operador, Guía y Transportista ("más de una categoría") |
| 0:29 | **Paso 3:** completa tus datos | Pestaña Datos: nombre, descripción, ubicación, teléfono, correo y WhatsApp se escriben en sincronía con la voz |
| 0:35 | **Paso 4:** sube tus documentos | Pestaña Credenciales: RUC, Licencia ATP y Seguro vigente se cargan con barra de progreso |
| 0:40 | **Paso 5:** envía tu solicitud | Pestaña Revisión y "Enviar solicitud"; luego "En revisión" que pasa a "Aprobado" con confeti |
| 0:45 | **Paso 6:** ¡comienza a crecer! | Panel de administración: reservas, clientes e ingresos que suben, gráfico animado, próximas reservas y píldoras de Reservas, Disponibilidad y Clientes |
| 0:55 | Comienza tu registro hoy | Navegador con la URL escribiéndose |
| 0:58 | Cabany: descubre, reserva y vive Panamá | Logo, lema y cabanypanama.com |

- **Seguimiento de pasos:** arriba aparecen los 6 pasos, con los completados marcados. Debajo van la etiqueta "PASO N" y el título en blanco con verde (Poppins).
- **Pantallas:** recreaciones nítidas y animadas basadas en las imágenes oficiales del cliente (panel "Ofrecer mis servicios" con pestañas 1 Tipo · 2 Datos · 3 Credenciales · 4 Revisión).
- **Sitio web:** al momento de editar, cabanypanama.com mostraba una verificación anti-bots incluso en la portada, así que no se pudo leer ni grabar de forma automática.

## Audio

- **Música:** la misma base original del tutorial de anfitriones (112 BPM). Baja automáticamente cuando habla la voz.
- **Efectos de la biblioteca del cliente** (`recursos/sfx/`):
  - whooshes en cada corte y en cada paso;
  - impactos en los títulos;
  - clics y tecleo en los formularios;
  - `contador_ticks` en las barras de carga y los números del panel;
  - notificaciones al terminar cada carga y en la aprobación;
  - riser en el logo, la aprobación y el cierre;
  - multitud que celebra en "Aprobado".
