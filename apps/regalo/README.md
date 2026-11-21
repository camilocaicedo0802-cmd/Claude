# Un regalo para ti

Página-regalo para tu pareja: se abre tocando un corazón y recorre la historia de los dos. Es un sitio estático (HTML, CSS y JS sin compilación), pensado para verse en el celular después de escanear un código QR.

## Qué trae

1. **Bienvenida**: tarjeta "Tienes un regalo" y un corazón que se llena con cada toque.
2. **Portada**: foto a pantalla completa con los nombres y la fecha.
3. **Nuestra canción**: disco que gira con una foto; suena al abrir el regalo.
4. **Galería**: carrusel de fotos.
5. **Carta**.
6. **Línea del tiempo**: contador de días juntos y los momentos importantes.
7. **Mensaje de voz**: reproductor con la forma de onda del audio.
8. **Mapa**: los lugares de la historia, con sus pines numerados.
9. **Última sorpresa**: tres preguntas que desbloquean un vale.

## Personalizar

Todo el contenido está en [`contenido.js`](contenido.js): nombres, fecha, textos, preguntas y el vale. No hace falta tocar nada más.

| Qué | Dónde |
| --- | --- |
| Fotos | Carpeta `fotos/`. Reemplaza los archivos o cambia las rutas en `contenido.js`. Verticales (3:4) para la galería; 1200 px de ancho es suficiente. |
| Canción | `cancion.spotify` con el enlace de Spotify, o `cancion.archivo` con un audio propio en `audio/`. |
| Mensaje de voz | Graba una nota de voz, guárdala en `audio/` y pon la ruta en `voz.archivo`. |
| Lugares | `lugares.puntos`, con `lat` y `lng` (en Google Maps: clic derecho sobre el lugar). |
| Preguntas | `sorpresa.preguntas`. `correcta` es la posición de la respuesta buena empezando en 0, o `"todas"`. |

Si borras una sección de `contenido.js` (o la dejas vacía), esa parte no aparece.

Para resaltar una palabra o frase en itálica, ponla entre asteriscos: `"Momentos que *no se borran*"`. Funciona en títulos, carta, preguntas y vale.

## Estilo

Amarillo y blanco con tinta casi negra. Textos en Poppins, títulos en Poppins Bold y palabras resaltadas en itálica con serifa. La itálica prevista es Scholar Italic; mientras no esté su archivo se usa Instrument Serif Italic, que es parecida. Los colores y las tipografías son las variables del inicio de [`estilos.css`](estilos.css).

Las fotos, la melodía y el mensaje de voz que vienen incluidos son de ejemplo.

## Verlo en tu computador

```bash
cd apps/regalo
python3 -m http.server 8080   # y abre http://localhost:8080
```

## Publicarlo

Sube la carpeta `apps/regalo` tal cual a cualquier hosting estático (Netlify, Vercel, Cloudflare Pages, GitHub Pages). Con la dirección final se genera el código QR de la tarjeta.

La página lleva `noindex`, así que los buscadores no la listan, pero cualquiera con el enlace puede abrirla. Este repositorio es público: lo que subas aquí (fotos, carta, audio) queda visible para cualquiera.

## Créditos

- Mapa: [Leaflet](https://leafletjs.com) (incluido en `vendor/`), teselas de CARTO con datos de OpenStreetMap y contorno de respaldo de Natural Earth.
- Tipografías: Poppins e Instrument Serif (Google Fonts).
