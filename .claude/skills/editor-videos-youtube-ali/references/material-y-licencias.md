# Material y licencias

El canal se monetiza: un reclamo de Content ID o una baja cuesta más que cualquier imagen. Ante la duda,
no se usa.

## Licencias aceptadas

| Aceptada | Condición |
| --- | --- |
| Dominio público (PD, Public Domain Mark) | Ninguna; se nombra la fuente en los créditos por cortesía. |
| CC0 | Ninguna. |
| Licencia Unsplash | Ninguna; se listan los autores en los créditos completos. Nunca Unsplash+ (de pago). |
| "No known copyright restrictions" (Flickr Commons, LoC) | Se nombra la institución. |
| United States Government Work | Se nombra la agencia. |
| CC BY 2.0 / 4.0 | **Atribución obligatoria**: autor, título, licencia con enlace y enlace a la foto, en la descripción (resumen) y en los créditos completos. |

Rechazadas siempre: CC BY-SA, cualquier NC o ND, "todos los derechos reservados", fotos sin licencia
clara, metraje de los videos de referencia, películas caseras sin licencia explícita.

## Comprobaciones de derechos que se hicieron en este chat

- **Library of Congress:** que el resultado sea "unrestricted" en la búsqueda solo significa que se puede
  ver en línea, no que esté libre. Para fotos posteriores a 1930 lee el campo `rights_advisory` del
  ítem (`<url>?fo=json`). La colección Vergara dice "Publication may be restricted": se quitó de Atlantic
  Avenue y se re-renderizó ese tramo. Carol M. Highsmith, Detroit Publishing, Bain, Harris & Ewing, HABS/HAER
  y todo lo anterior a 1930 son dominio público.
- **Películas de archivo (Prelinger / Internet Archive):** aunque estén marcadas como dominio público,
  pueden recibir reclamos automáticos de quien subió la misma película. Se usaron poco y recortadas en
  I-80, Cumberland y Donner; en Atlantic Avenue no se usaron. La película del NPS de 1979 sobre Cumberland
  Gap se descartó porque su música tenía derechos reservados. Una película de Castle Films (1946) con © en
  pantalla, aunque marcada PD, se dejó fuera.
- **Música:** Kevin MacLeod (CC BY 4.0) se usó en los cuatro primeros episodios y uno recibió un reclamo de
  copyright. Ya no se usa. Ver `audio-y-musica.md`.
- **Personas y marcas:** no pongas el nombre de alguien sobre la cara de otra persona; si no hay retrato
  libre de una persona, usa una tarjeta tipográfica. Evita fotos de stock con marcas visibles (se quitó una
  tapa de alcantarilla con logotipo "TWA") y no nombres marcas en pantalla si no hace falta (en la
  narración salía Trader Joe's; en pantalla se puso "UN SUPERMERCADO").
- **Recreaciones:** documentos, planos, permisos, chats o nóminas dibujados por nosotros llevan la
  etiqueta "RECREACIÓN" o "Ilustración", y se dice en la descripción.

## Fuentes y cómo comportarse con cada una

| Fuente | Qué aporta | Notas |
| --- | --- | --- |
| Unsplash (MCP) | Fotos de stock modernas de calidad (2400 px) | Hazlo con un subagente: devuelve solo un resumen y no llena el contexto. Unas 6 fotos por consulta, 40–50 consultas. |
| Library of Congress | Grabados, fotos históricas, estereografías, Highsmith | La búsqueda es lenta y a veces da 429: déjala correr en segundo plano. Para Prints & Photographs, la miniatura es el `r.jpg` del almacén y la descarga es el maestro `u.tif` si pesa menos de 150 MB, si no `v.jpg`. |
| Flickr | Fotos de visitantes y de instituciones (Flickr Commons) | `fl.py` filtra licencias 4 (CC BY 2.0), 7 (sin restricciones), 8 (gobierno EE. UU.), 9 (CC0), 10 (PDM), 11 (CC BY 4.0). Descarga con `FL_SLEEP=10` (si no, 429). No cambies el user-agent para esquivar bloqueos. Algunas fotos solo bajan a 800 px: úsalas enmarcadas (`fr()`). |
| Wikimedia Commons | Algo de PD y CC BY | Casi todo es CC BY-SA (no sirve). Respeta su política de robots: tamaños estándar de miniatura (960, 1280, 1920…), `Retry-After`, como mucho 2 descargas a la vez. |
| Internet Archive | Películas PD | Elige el mp4/mpeg de más resolución; los mpeg anamórficos 352×480 se pasan a píxel cuadrado con `scale=trunc(ih*dar/2)*2:ih,setsar=1`. Clips siempre dentro de una sola escena (`scenes.sh`). |
| NYC Open Data, Natural Earth, Mapzen | Calles, costas, límites, relieve | Libres; se citan en los créditos. |

No se puede usar: Pixabay y Mixkit (tienen protección contra bots y la API de Pixabay pide clave), ni
intentar saltarse esa protección. Si hace falta algo de ahí, se le pide a Ali que lo descargue y lo suba.

## Privacidad

Las herramientas de descarga se identifican con un user-agent genérico ("DPDoc/1.0" o
"DocResearchBot/1.0"); no pongas el correo de Ali ni ningún dato personal en las cabeceras ni en el código
que se sube al repositorio.

## Registro

Cada fuente deja su registro en `work/` (`unsplash.json`, `loc.json`, `flickr.json`, `films.json`) y
`tools/usados.py` genera `work/used.json` con lo que de verdad aparece en el video. De ahí salen los
créditos (`tools/creditos.py`). Copia a `data/credits_used.json` del repositorio solo las entradas usadas.
