# Créditos de material de terceros

## Fotografías (recortadas con BiRefNet y pasadas a escala de grises)
| Archivo en `video/public/img` | Título original | Autor | Licencia | Fuente |
|---|---|---|---|---|
| hourglass_light.png | Wooden hourglass 3 | S Sepp | CC BY-SA 3.0 | https://commons.wikimedia.org/w/index.php?curid=2949887 |
| hourglass_dark.png | Low Key running hourglass | Tijs Zwinkels | CC BY-SA 2.0 | https://www.flickr.com/photos/41668395@N04/3988939596 |
| coins_stacks.png | Stacks of pound coins | Images_of_Money | CC BY 2.0 | https://www.flickr.com/photos/59937401@N07/5930116778 |
| coins_rising.png | Coins | Images_of_Money | CC BY 2.0 | https://www.flickr.com/photos/59937401@N07/5929568821 |
| watch_light.png | Portrait of a Pocket Watch | cdsessums | CC BY-SA 2.0 | https://www.flickr.com/photos/53313745@N00/10088293633 |
| watch_dark.png | Vintage American Watch Company Bond Street Pin Set Pocket Watch | France1978 | CC BY-SA 2.0 | https://www.flickr.com/photos/51764518@N02/8675151837 |
| bust_marcus.png | Marcus Aurelius (Museo del Prado) 01 | Zaqarbal | CC BY-SA 2.0 | https://www.flickr.com/photos/44949176@N00/232013720 |
| brain.png | The Human Brain Model 02 | Edeh Sophia | CC0 1.0 | https://commons.wikimedia.org/w/index.php?curid=142150327 |

Encontradas con Openverse (solo licencias que permiten uso comercial y modificación).
Si publicas el vídeo, añade en la descripción: «Imágenes: S Sepp, Tijs Zwinkels, Images_of_Money, cdsessums, France1978, Zaqarbal (CC BY / CC BY-SA)».

## Audio
- **Música:** cama musical extraída del vídeo de referencia (`referencia/referencia.mp4`) separando la voz con Demucs (htdemucs_ft) y alargada en bucle. Los derechos son los de la pista original de la referencia.
- **SFX `ref_*`:** extraídos del vídeo de referencia (whooshes / impactos).
- **SFX `rm_*`:** biblioteca oficial de Remotion (https://remotion.media).
- **SFX `tick`, `boom`, `blip`, `pop`, `swipe`, `whoosh_long`, `riser`, `scribble`, `sand`:** sintetizados con `assets/tools/audio_build.py`.

## Tipografías (SIL Open Font License)
- Archivo (Omnibus-Type), Parisienne (Astigmatic) — vía Fontsource.

## Modelos
- Whisper medium (OpenAI, MIT) para la transcripción.
- Demucs htdemucs_ft (Meta, MIT) para separar voz y música.
- BiRefNet (MIT) para recortar fondos.
