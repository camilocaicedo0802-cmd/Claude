# Audio y música

## Lo que pidió Ali

En los dos episodios seguidos pidió "bájale un poco a la música y sonidos para que no opaque la voz del
narrador". La voz manda: la música acompaña muy por debajo y los efectos son casi subliminales. Después,
por un reclamo de copyright, pidió música de la Biblioteca de audio de YouTube Studio.

## Niveles que quedaron aprobados

| Elemento | Ajuste en `audio.py` | Medida (stem antes de normalizar) |
| --- | --- | --- |
| Pistas de música | cada pista llevada a ≈ −27,5 LUFS con su ganancia: `-27.5 - LUFS_pista` | — |
| Ducking bajo la voz | `duck(depth_db=-9.0, attack=0.08, release=0.6)` | — |
| Bus de música | `music * db(0.5)` | pista de música ≈ −34,5 LUFS (≈ −33 tras normalizar) |
| Efectos | `sfx * db(-11)` | ≈ −36 LUFS |
| Voz | `db(0)` | mezcla ≈ −15 LUFS; el final se normaliza a −14 LUFS, pico −1,5 dBTP |

Historia de los ajustes (para no repetirlos): en Laurel Hill la música quedó baja y se subió (stem −29);
en I-80 se dejó en −29,5 con bus +1,5 y efectos −7; en Cumberland, al pedir Ali bajarla, bus +1,5 con
pistas más bajas (stem −33,3) y efectos −11; en Donner y Atlantic, bus +0,5 y efectos −11. No la subas
por encima de esto sin que Ali lo pida.

## Pistas de YouTube Studio (preferido)

Al empezar el episodio, mándale este pedido (adaptando los capítulos al guion):

> En YouTube Studio entra en **Biblioteca de audio → Música**, filtra por **Atribución no obligatoria**,
> descarga **9 pistas** de al menos 2–3 minutos y súbemelas aquí:
>
> | # | Parte del video | Género | Ánimo |
> | --- | --- | --- | --- |
> | 1 | Intro (misterio) | Cinemática o Ambiental | Oscuro |
> | 2 | Capítulo de contexto histórico, ligero | Country y folk o Clásica | Alegre o Brillante, suave |
> | 3 | Capítulo de conflicto | Cinemática | Dramático |
> | 4 | Rumores, crimen, intriga | Jazz y blues | Oscuro |
> | 5 | Investigación, descubrimiento | Cinemática o Ambiental | Inspirador |
> | 6 | El momento clave, suspenso | Cinemática | Oscuro o Dramático |
> | 7 | Pérdida, cierre | Cinemática o Clásica | Triste o Dramático |
> | 8 | Hoy | Ambiental | Tranquilo |
> | 9 | Conclusión | Clásica o Cinemática (piano) | Triste o Inspirador |

Guarda las pistas en `assets/yt/`, mide su loudness y escribe `work/music.json`:
`[[inicio, fin, "yt/archivo.mp3", desplazamiento_s, ganancia_dB], …]`, un hueco por capítulo que se solapa
1–1,5 s con el siguiente (fundido de entrada 2 s, de salida 3 s; si la pista es más corta que el hueco, se
repite desde el segundo 8). En la descripción: "Música: Biblioteca de audio de YouTube".

## Banda sonora original (`score.py`, si no llegan las pistas)

`$PY edit/score.py assets/score L1 … L9` genera `cue_1.wav … cue_9.wav` con la duración de cada hueco
(+4 s). Todo se sintetiza aquí (sin muestras): acordes de sierra con banda limitada, cuerdas pulsadas,
piano aditivo, campanas, bajo, bombo, timbal, escobillas, trémolo y reverb por convolución.

| Pieza | Carácter |
| --- | --- |
| 1 `cue_dark` | dron grave, pulso, campanas sueltas |
| 2 `cue_street` | arpegios de cuerda pulsada en re mayor, folk |
| 3 `cue_drama` | ostinato en la menor (Am–F–G–E) con timbal |
| 4 `cue_noir` | bajo caminante, escobillas, acordes m7 (estilo cine negro) |
| 5 `cue_quest` | arpegio pulsante lidio, en ascenso |
| 6 `cue_tension` | latido grave, trémolo cromático |
| 7 `cue_sad` | acordes menores lentos con melodía de piano |
| 8 `cue_calm` | colchón aéreo y campanas |
| 9 `cue_end` | arpegios de piano de menor a mayor |

No se puede escuchar desde aquí: revisa loudness (ebur128) y un espectrograma de cada pieza (líneas
armónicas limpias, sin ruido de aliasing). La primera versión usaba sierras ingenuas y tenía mucho ruido
agudo: por eso los acordes usan tablas de onda con armónicos limitados. En la descripción: "Música: banda
sonora original, compuesta y sintetizada para este video".

## Efectos de sonido (todos sintetizados en `audio.py`)

- **Automáticos desde la línea de tiempo:** whoosh en `whip`/`zoom`, estática en `glitch`, golpe en
  `flash`, subida + boom en cada tarjeta de capítulo, boom + golpe en cada `Stamp`, golpe en `BigText` con
  `pop`, tics en `Counter`.
- **A mano por episodio** (bloque "handcrafted beds" de `build_sfx`): goteo en túneles, viento, autobuses y
  tráfico, frenazo, cascos de caballo, locomotora de vapor (`chuff`) y silbato, picos y palas (`clank`),
  martillo neumático, sirena, radio (estática), latido en el suspenso, tapa de alcantarilla (`scrape`),
  arrastrarse, pitidos de escáner, motores, retumbos de explosiones. Ánclalos con `w("palabra", seg)`.
- Ganancias individuales entre −8 y −21 dB, y luego todo el bus a −11 dB.

## Cambiar la música de un episodio ya entregado

Solo hace falta el audio: guarda las pistas nuevas, reescribe `work/music.json`, vuelve a correr
`audio.py` y luego `splice.py` (o, más rápido, mezcla el `mix.wav` nuevo normalizado con el video del
máster con `-c:v copy`). Después, partes y archivo optimizado de nuevo (≈30–40 min en total, sin render).
