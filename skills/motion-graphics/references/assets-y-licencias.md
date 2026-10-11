# Recursos visuales y licencias

## Elegir el tipo de recurso

Usa el mismo tipo de recurso que la referencia:

| La referencia usa… | Haz… |
|---|---|
| fotos recortadas con sombra | `find_images.py` + `cutout.py` |
| fotos o vídeo a sangre | `find_images.py` (fotos horizontales o verticales de alta resolución) o clips del usuario |
| iconos planos o emojis | SVG propios (formas simples) o la fuente Noto Color Emoji |
| maquetas de UI (móvil, notificaciones, navegador) | componentes vectoriales (`Phone`, `Notification`, `VideoThumb`) |
| ilustraciones | SVG propios o imágenes con licencia del mismo estilo |
| 3D | `@remotion/three` (skill oficial `remotion-markup/3d.md`) o fotos de objetos con iluminación parecida |

**Metáfora:** cada objeto debe simbolizar lo que dice la voz en ese momento.
- tiempo → reloj de arena o de bolsillo;
- dinero → monedas o billetes;
- atención → ojo o cerebro;
- peligro → señal de advertencia;
- móvil o redes → teléfono y notificaciones;
- reflexión → estatua o busto clásico;
- crecimiento → pilas crecientes o flecha.

Busca en inglés: hay más resultados.

## Buscar imágenes con licencia

```bash
python3 scripts/find_images.py search "hourglass white background" cand/reloj   # hoja cand/reloj/sheet.png
python3 scripts/find_images.py get cand/reloj 12 --out assets/raw --name reloj     # descarga + credits.json
python3 scripts/find_images.py credits assets/raw/credits.json                     # tabla para CREDITOS.md
```

- Openverse filtra por `license_type=commercial,modification` (CC0, PDM, BY, BY-SA). Las licencias NC/ND no se usan.
- Elige imágenes con el objeto entero, nítido, poco cortado y con fondo simple: el recorte sale mejor. «isolated», «white background», «on black» y «studio» ayudan en la búsqueda.
- Límites de Openverse: 20 peticiones/min y 200/día sin clave. Wikimedia limita ráfagas (429) y exige un User-Agent descriptivo; el script espera y reintenta. Si `upload.wikimedia.org` devuelve 429, usa la miniatura de 1280 px (`/thumb/.../1280px-...`).
- Las BY y BY-SA requieren atribución: genera `CREDITOS.md` y dale al usuario la línea para la descripción.
- Las marcas, logotipos y caras reconocibles de personas reales no se usan como b-roll salvo que el usuario aporte el material o sea claramente informativo.

## Recortar y tratar

```bash
python3 scripts/cutout.py assets/raw/reloj.jpg public/img/reloj.png --mono            # B/N con autocontraste
python3 scripts/cutout.py assets/raw/producto.jpg public/img/producto.png              # color natural
python3 scripts/cutout.py assets/raw/foto.jpg public/img/foto.png --tint "#1E3A8A"     # duotono hacia la paleta
python3 scripts/cutout.py assets/raw/ public/img/ --mono                               # lote
```

- BiRefNet (MIT) se descarga una vez (~970 MB; `--lite` ~220 MB) a `~/.cache/motion-graphics/`.
- Revisa los recortes sobre el fondo del vídeo (hoja de contactos) antes de usarlos: manos, bases y peanas sobrantes se pueden recortar con PIL (`crop`) o tapar con encuadre.
- Mide puntos de anclaje (ojos, cuellos, centros de esfera) superponiendo una cuadrícula con PIL. Sirven para colocar barras, partículas o halos en coordenadas de la imagen escaladas.
- Registra el tamaño natural de cada recorte en `IMG` (`components/Cutout.tsx`).

## Vectoriales

Si una foto no existe o no encaja (UI, tarjetas, señales, gráficos de datos, flechas), dibújala con divs y SVG con la misma estética: misma paleta, misma sombra y mismo grosor de línea que la referencia. Los componentes `Phone`, `CreditCard`, `WarningSign`, `LoopArrow`, `Notification` y `VideoThumb` son ejemplos de partida.

## Créditos

`CREDITOS.md` en la raíz del proyecto debe incluir:

- tabla de imágenes con autor, licencia y fuente;
- música (si es de la referencia: «extraída de la referencia, derechos de su autor»);
- SFX (Remotion, sintéticos, de la referencia);
- fuentes (OFL);
- modelos usados (Whisper, Demucs, BiRefNet: MIT).
