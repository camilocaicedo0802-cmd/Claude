# Tutorial Cabany · "¿Tienes una cabaña? Conviértela en ingresos"

Video vertical en modo tutorial (1080×1920, 30 fps, 64 s). Explica cómo publicar una cabaña en cabanypanama.com y cómo se reciben los pagos, con voz de Google AI.

- `cabany_tutorial_anfitrion.mp4`: video final (H.264 + AAC 48 kHz, −14 LUFS).
- `portada.jpg`: cuadro de muestra (paso 3).
- `guion/guion.txt`: texto narrado.
- `guion/voz_gemini_sulafat.wav`: voz sola, ya editada.
- `fotos_cliente/`: las 6 imágenes del cliente (Paso 1–5, Pagos y cortes) que sirvieron de base.
- `proyecto/work/`: código que genera el video.

## Voz

- **Modelo:** Google Gemini TTS (`gemini-3.8-flash-tts`), voz **Sulafat**, en español latino.
- **Indicación de estilo:** guía cálida y entusiasta de redes sociales, ritmo ágil y natural, pronunciando "Cabany" como "Kabáni".
- **Edición:** se acortaron los silencios largos (más de 0.3 s) y se aceleró un 8 % sin cambiar el tono. La duración bajó de 72 s a 62 s de narración.
- **Alternativa:** también se generó la voz **Laomedeia**. Se puede cambiar en `tts.py`.

## Estructura

| Tiempo | Voz | Pantalla |
| --- | --- | --- |
| 0:00 | ¿Tienes una cabaña? ¡Conviértela en ingresos con Cabany! | Cabaña real a pantalla completa, "cabaña?" e "ingresos" en verde gigante, billetes y monedas, logo |
| 0:04 | Publica tu alojamiento y recibe reservas de turistas | Tarjeta "¡Propiedad aprobada!" y notificaciones de "¡Nueva reserva!" que caen una tras otra |
| 0:09 | Te enseño cómo funciona, paso a paso | "¿Cómo funciona?" y círculos 1–5 |
| 0:11 | **Paso 1:** entra y haz clic en Registrarse | Navegador 3D con la página: se escribe la URL, zoom al botón "Registrarse", cursor y clic |
| 0:17 | **Paso 2:** completa tus datos | Formulario "Registro de Anfitrión": cada campo se llena al decirlo (nombre, correo, teléfono, contraseña), clic en "Crear cuenta" y confeti |
| 0:23 | **Paso 3:** publica tu cabaña | Panel "Agregar nueva propiedad": la cámara recorre cada sección mientras se nombra (fotos, ubicación, capacidad, servicios, precio, disponibilidad) y una píldora indica cuál es |
| 0:30 | **Paso 4:** revisa y envía | "Revisión final": los checks se marcan y clic en "Enviar para verificación" |
| 0:34 | **Paso 5:** verificación y aprobación | "Solicitud en revisión" con indicador de carga, giro a "¡Propiedad aprobada!" con confeti y la cabaña "Nuevo" en la página |
| 0:40 | ¿Cómo recibes tus pagos? | Cabany gestiona el cobro (tarjeta de reserva); calendario con los lunes marcados; línea de tiempo Lunes → 1–2 días → Hasta 4 días → Pago disponible |
| 0:51 | Publicar no tiene costo | Sello "GRATIS" con confeti |
| 0:54 | Tú tienes la cabaña; nosotros te conseguimos huéspedes | Foto de la cabaña e íconos de viajeros |
| 0:57 | Regístrate hoy | Navegador con la URL escribiéndose |
| 0:59 | Cabany: descubre, reserva y vive Panamá | Logo, lema y cabanypanama.com |

- **Seguimiento de pasos:** arriba siempre se ven los cinco pasos, con los completados marcados. Debajo van la etiqueta "PASO N" y el título en blanco con verde (Poppins).
- **Pantallas:** son recreaciones nítidas, animadas y fieles a las imágenes oficiales del cliente. La sección de anfitriones del sitio real tiene una verificación anti-bots, así que no se pudo grabar en vivo.

## Audio

- **Voz:** Gemini TTS (ver arriba).
- **Música:** original, pop-chill a 112 BPM en Sol mayor (bombo, chasquidos, rhodes y arpegio). Baja automáticamente cuando habla la voz.
- **Efectos:** de la biblioteca del cliente (`recursos/sfx/cliente`).
  - `whoosh_largo` en cada cambio de paso.
  - `impacto_bajo` y `pop` en cada título.
  - `click` en botones y teclas, con tecleo real en cada campo.
  - `notificacion` en las reservas y la aprobación.
  - `cash_register` en "ingresos", el cobro y "gratis".
  - `contador_ticks` en el calendario y la línea de tiempo de pago.
  - `riser` en la aprobación y el cierre.
  - `multitud_celebra` en la aprobación y en "no tiene costo".
