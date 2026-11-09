# Reel Cabany 3 · "Reserva desde ya"

Video vertical (1080×1920, 30 fps, 31 s) editado desde el crudo en 4K (`Video crudo` de Drive, 34.6 s). Sigue el estilo de `Video_de_referencia_Cabany_2.mp4`, con textos blancos y resaltes verdes.

- `cabany_reel_3.mp4`: video final (H.264 + AAC 48 kHz, −14 LUFS).
- `portada.jpg`: cuadro de muestra.
- `proyecto/work/`: el código que genera el video.

## Estructura (calcada de la referencia)

| Tiempo | Referencia | En este video |
| --- | --- | --- |
| 0:00–0:04 | "People only / SPEND MONEY" + caja con "$$$" brillante + círculos ① ② ③ | "reserva / DESDE YA" + caja brillante con tres casas verdes; "www. / cabanypanama.com"; círculos ① ② ③ |
| 0:04 | "1 SOLUTIONS" | **1 ENTRA**, y luego el teléfono 3D con la página ("en nuestra plataforma") |
| 0:05 | "$" fantasma gigante detrás de él | Checks fantasma gigantes detrás de él: "es totalmente / fácil" |
| 0:07 | "2 CONVENIENCE" + íconos en cajas punteadas | **2 ESCOGE** + cajas con foto de cabaña y hotel ("CABAÑA", "HOTEL") |
| 0:09 | "$30 toaster" en caja punteada | **3 PAGA** + cajas "Yappy" y "Visa", con caja registradora |
| 0:15 | Gráfico de barras 3D de empresas | Gráfico 3D "Temporada alta": Fiestas Patrias 🇵🇦, Fin de año 🎆, Feria de las Flores 🌸, con ambiente de fiesta |
| 0:19 | Clips de película | Cortes rápidos de cabañas reales ("para poder / reservar / tu cabaña") |
| 0:21 | Contador "$10,000" | Contador de personas: aparecen 8 en "grupos grandes" y quedan 2 en "pequeños" |
| 0:27 | Barra "Follow" con cursor | Barra de comentario donde se escribe "RESERVA", con cursor y "Enviar" |

## Edición

- **Cortes:** se quitó el conteo "3, 2, 1" del inicio y se recortó cada pausa con cortes secos (13 tomas). En cada corte cambia el encuadre (golpe de zoom), con acercamiento lento dentro de cada toma.
- **Encuadre:** se usa la fuente 4K, así que los acercamientos no pierden nitidez. El encuadre sigue la cabeza del presentador con la cabeza a ~27 % de altura, como en la referencia.
- **Tipografía:** Poppins.
  - SemiBold blanca para las frases.
  - ExtraBold verde (degradado #C8F56A → #5CB82C con brillo) para las palabras clave.
  - ExtraBold Italic blanca en mayúsculas para los pasos.
  - Las palabras entran con un golpe de escala y desenfoque, y salen con un desvanecido rápido.
- **Gradación:** más contraste, tono cálido y viñeta inferior.
- **Marca de agua:** logo pequeño y URL arriba a la derecha.

## Audio

- **Voz:** la del crudo, nivelada, con los cortes cruzados en 12 ms.
- **Música:** original, hip-hop oscuro a 92 BPM en Do menor (808, caja, palmas, hats con redobles, campana y pad). Se corta en seco antes de la URL, como el silencio de la referencia, y vuelve con un impacto. Cierra con un golpe final.
- **Efectos del cliente** (`recursos/sfx/cliente`):
  - `whoosh_corto` en palabras clave y cortes;
  - `whoosh_largo` en transiciones;
  - `pop` en casas, círculos y pilares;
  - `click` en cajas, tecleo y enviar;
  - `cash_register` en "pagas";
  - `contador_ticks` en el contador de personas;
  - `impacto_bajo` en los números, la URL, el gráfico y "RESERVA";
  - `riser` hacia el gráfico y hacia "RESERVA";
  - `notificacion` en "fácil" y al enviar el comentario.
- **Ambiente de fiesta** (`recursos/sfx/ambiente`, Mixkit): fuegos artificiales, multitud celebrando, feria y bar lleno bajo el gráfico de temporadas.
