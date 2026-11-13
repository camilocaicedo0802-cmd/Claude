// Guion de edición del video 1 ("Nadie le compra a tu negocio").
// Todos los tiempos en SEGUNDOS de la línea de tiempo final, anclados a palabras
// (ws(i) = inicio de la palabra i en timeline.ts). Si cambian los cortes, todo se reajusta.
import {SPEECH_FRAMES, WORDS} from './timeline';
import {ws, we} from './helpers';

export const TAIL = 1.9; // segundos de cierre tras la última palabra
export const TOTAL_SECONDS = SPEECH_FRAMES / 30 + TAIL;

// ---------- Encuadre de cada segmento hablado (punch-in alterno, estilo.md §6-7) ----------
// scale: [inicio, fin] del segmento. zoom: zoom animado (gancho).
export type Framing = {scale: [number, number]; y?: number; zoom?: {from: number; to: number; s: number; e: number}};
export const FRAMING: Record<number, Framing> = {
  // corrección §10.2: máximo 1,3× para que la barbilla quede por encima de los subtítulos
  0: {scale: [1, 1], zoom: {from: 1.0, to: 1.28, s: 0.35, e: 1.55}},
  1: {scale: [1.28, 1.3]},
  2: {scale: [1.0, 1.04]},
  3: {scale: [1.2, 1.24]},
  4: {scale: [1.3, 1.3]},
  5: {scale: [1, 1.03]},
  6: {scale: [1, 1.03]},
  7: {scale: [1, 1.03]},
  8: {scale: [1.26, 1.3]},
  9: {scale: [1.05, 1.1]},
  10: {scale: [1.2, 1.24]},
  11: {scale: [1, 1.03]},
  12: {scale: [1, 1.03]},
  13: {scale: [1, 1.03]},
  14: {scale: [1, 1.03]},
  15: {scale: [1.24, 1.28]},
  16: {scale: [1.0, 1.03]},
  17: {scale: [1.16, 1.2]},
  18: {scale: [1.24, 1.28]},
  19: {scale: [1.05, 1.08]},
  20: {scale: [1.26, 1.3]},
  21: {scale: [1.0, 1.04]},
  22: {scale: [1.0, 1.03]},
  23: {scale: [1, 1.02]},
  24: {scale: [1, 1]},
};

// ---------- Títulos grandes (estilo.md §3 + §10) ----------
export type TitleWord = {text: string; at: number};
export type TitleLine = {words: TitleWord[]; color: 'white' | 'purple' | 'chrome'; size: number; upper?: boolean; dx?: number};
export type TitleDef = {
  id: string;
  start: number;
  end: number;
  /** centro vertical en px; 'head' = se ancla a la cabeza del plano (el bloque queda encima y solapa `overlap` px detrás de él) */
  y: number | 'head';
  overlap?: number;
  lines: TitleLine[];
  /** en escena: sigue el zoom de cámara y va DETRÁS de la persona (máscara) */
  scene?: boolean;
  tilt?: number; // rotateX en grados
  covers: number[]; // índices de palabras que NO llevan subtítulo pequeño
};
const tw = (i: number, text?: string): TitleWord => ({text: text ?? WORDS[i].text.replace(/[,.¿?]/g, '').toLowerCase(), at: ws(i)});

export const TITLES: TitleDef[] = [
  {
    id: 'gancho', start: ws(0), end: ws(7) - 0.03, y: 'head', overlap: 70, scene: true,
    lines: [
      {words: [tw(0, 'nadie,'), tw(1), tw(2)], color: 'purple', size: 72, dx: -20},
      {words: [tw(3), tw(4), tw(5), tw(6)], color: 'white', size: 80, dx: 40},
    ],
    covers: [0, 1, 2, 3, 4, 5, 6],
  },
  {
    id: 'producto', start: ws(11), end: ws(16) - 0.03, y: 600,
    lines: [
      {words: [tw(11), tw(12), tw(13)], color: 'white', size: 112},
      {words: [tw(14), tw(15)], color: 'purple', size: 136},
    ],
    covers: [11, 12, 13, 14, 15],
  },
  {
    id: 'otro', start: ws(33), end: ws(37) - 0.03, y: 'head', overlap: 90, scene: true,
    lines: [
      {words: [tw(33), tw(34)], color: 'white', size: 104},
      {words: [tw(35), tw(36)], color: 'purple', size: 150},
    ],
    covers: [33, 34, 35, 36],
  },
  {
    id: 'personas', start: ws(38), end: ws(43) - 0.03, y: 400,
    lines: [
      {words: [tw(38), tw(39)], color: 'white', size: 100},
      {words: [tw(40), tw(41), tw(42)], color: 'purple', size: 118},
    ],
    covers: [38, 39, 40, 41, 42],
  },
  {
    id: 'comprar', start: ws(46), end: ws(49) - 0.03, y: 560,
    lines: [
      {words: [tw(46), tw(47)], color: 'white', size: 112},
      {words: [tw(48)], color: 'purple', size: 150},
    ],
    covers: [46, 47, 48],
  },
  {
    id: 'redes', start: ws(51), end: ws(55) - 0.03, y: 330,
    lines: [
      {words: [tw(51), tw(52)], color: 'white', size: 100},
      {words: [tw(53), tw(54)], color: 'purple', size: 118},
    ],
    covers: [51, 52, 53, 54],
  },
  {
    id: 'venta', start: ws(79), end: ws(82) - 0.03, y: 'head', overlap: 80, scene: true,
    lines: [
      {words: [tw(79)], color: 'purple', size: 150},
      {words: [tw(80), tw(81)], color: 'white', size: 112},
    ],
    tilt: 16,
    covers: [79, 80, 81],
  },
  {
    id: 'importante', start: ws(88), end: ws(90) - 0.12, y: 'head', overlap: 80, scene: true,
    lines: [
      {words: [tw(88)], color: 'chrome', size: 100},
      {words: [tw(89)], color: 'purple', size: 140},
    ],
    covers: [88, 89],
  },
  {
    id: 'perciben', start: ws(90), end: ws(99) - 0.03, y: 300,
    lines: [
      {words: [tw(90), tw(91)], color: 'chrome', size: 104},
      {words: [tw(92)], color: 'purple', size: 150},
    ],
    covers: [90, 91, 92],
  },
  {
    id: 'tecompra', start: ws(104), end: ws(109) - 0.03, y: 330,
    lines: [
      {words: [tw(104), tw(105), tw(106)], color: 'white', size: 96},
      {words: [tw(107), tw(108)], color: 'purple', size: 140},
    ],
    covers: [104, 105, 106, 107, 108],
  },
  {
    id: 'nocompra', start: ws(109), end: ws(113) - 0.03, y: 'head', overlap: 90, scene: true,
    lines: [
      {words: [tw(109), tw(110), tw(111)], color: 'white', size: 104},
      {words: [tw(112)], color: 'purple', size: 156},
    ],
    covers: [109, 110, 111, 112],
  },
  {
    id: 'perdiendo', start: ws(121), end: ws(127) - 0.03, y: 360,
    lines: [
      {words: [tw(121)], color: 'purple', size: 140},
      {words: [tw(125), tw(126)], color: 'white', size: 112},
    ],
    covers: [121, 125, 126],
  },
  {
    id: 'ayudemos', start: ws(132), end: ws(134) - 0.03, y: 400,
    lines: [
      {words: [tw(132)], color: 'white', size: 110},
      {words: [tw(133)], color: 'purple', size: 150},
    ],
    covers: [132, 133],
  },
  {
    id: 'ayuda', start: ws(134) + 0.2, end: ws(138) - 0.03, y: 'head', overlap: 110, scene: true,
    lines: [
      {words: [{text: 'escribe', at: ws(134) + 0.25}], color: 'chrome', size: 96, dx: -60},
      {words: [{text: 'AYUDA', at: ws(137)}], color: 'purple', size: 240, upper: true, dx: 20},
    ],
    covers: [134, 135, 136, 137],
  },
];

// Rangos donde se ocultan los subtítulos pequeños (escenas con texto propio)
export const NO_SUBS: [number, number][] = [
  [ws(24), ws(28) - 0.02], // palabras tachadas en pantalla
  [ws(68), ws(78) - 0.02], // nota escribiéndose en la escena CONFIANZA
  [ws(138), 999], // tarjeta final
];

// ---------- B-roll a pantalla completa ----------
export type BrollDef = {src: string; start: number; end: number; trim?: number; bw?: boolean; zoom?: [number, number]};
export const BROLL: BrollDef[] = [
  {src: 'broll/empaque.mp4', start: ws(7), end: ws(16), trim: 1.0, zoom: [1.08, 1.0]},
  {src: 'broll/personas.mp4', start: ws(37), end: ws(43), trim: 0.5, zoom: [1.0, 1.08]},
  {src: 'broll/compra_online.mp4', start: ws(43), end: ws(49), trim: 1.5, zoom: [1.1, 1.0]},
  {src: 'broll/mujer_movil.mp4', start: ws(57), end: ws(68), trim: 0.3, zoom: [1.0, 1.12]},
  {src: 'broll/bts_gimbal.mp4', start: ws(127), end: ws(131), trim: 0, zoom: [1.0, 1.06]},
  {src: 'broll/bts_grabacion.mp4', start: ws(131), end: ws(134), trim: 2.0, zoom: [1.08, 1.0]},
];

// ---------- Ventanas/tarjetas con clip horizontal sobre fondo desenfocado ----------
export type CardDef = {src: string; start: number; end: number; trim?: number; y: number; width: number; aspect: number; bw?: boolean; rotate?: number};
export const CARDS: CardDef[] = [
  {src: 'broll/precio.mp4', start: ws(23), end: ws(28), trim: 4, y: 560, width: 860, aspect: 16 / 9, rotate: -3},
  {src: 'broll/pago_tarjeta.mp4', start: ws(104), end: ws(109), trim: 3, y: 1300, width: 900, aspect: 16 / 9, rotate: 2},
  {src: 'broll/sin_ventas.mp4', start: ws(118), end: ws(127), trim: 1, y: 1400, width: 780, aspect: 1, bw: true, rotate: -2},
];

// ---------- Escenas de motion graphics ----------
export const SCENES = {
  tachado: {start: ws(23) + 0.02, end: ws(28), precios: ws(24), producto: ws(27), strike1: ws(25), strike2: ws(27) + 0.4},
  // corrección §10.2: entra cuando se tapa la boca con el dedo (17,1 s) para que no parezca desincronizado
  movil: {start: ws(50) - 0.08, end: ws(55)},
  hud: {start: ws(57), end: ws(68), confiar: ws(62), noConfiar: ws(66)},
  confianza: {start: ws(68), end: ws(78), t1: ws(74), t2: ws(77), noteStart: ws(68) + 0.1, noteText: 'Tu perfil no transmite confianza… ni profesionalismo'},
  collage: {start: ws(90) - 0.08, end: ws(99)},
  comentario: {start: ws(134), end: ws(138), typeAt: ws(137) - 0.1},
  final: {start: ws(138), words: [{t: 'te mandamos', at: ws(139)}, {t: 'mucho más', at: ws(141)}, {t: 'información', at: ws(143)}]},
};

// Fondo desenfocado y oscurecido (defocus) sobre el video hablado, para tarjetas y MG
export const DEFOCUS: [number, number][] = [
  [SCENES.movil.start, SCENES.movil.end],
  [ws(104), ws(109)],
  [ws(118), ws(127)],
];

// ---------- Transiciones ----------
export const FLASHES = [ws(50) - 0.08, ws(68), ws(127), ws(138)];
export const WHIPS = [ws(43), ws(57), ws(90) - 0.08];
export const BLUR_PULSES = [ws(16), ws(37), ws(82), ws(104)];

// ---------- Música (estilo.md §8: corte en seco tras el remate del gancho) ----------
export const MUSIC = {volume: 0.078, stopFrom: we(6) + 0.04, stopTo: ws(7), duckEnd: TOTAL_SECONDS - 0.9};

// ---------- Efectos de sonido ----------
export type Sfx = {src: string; at: number; vol: number; dur?: number; trim?: number};
const titleSfx: Sfx[] = TITLES.flatMap((t, ti) =>
  t.lines.flatMap((l, li) =>
    l.words.slice(0, 1).map((w) => ({
      src: ['sfx/whoosh_a.wav', 'sfx/whoosh_b.wav', 'sfx/whoosh_c.wav'][(ti + li) % 3],
      at: w.at - 0.06,
      vol: l.color === 'purple' ? 0.32 : 0.24,
      dur: 0.7,
    })),
  ),
);
export const SFX: Sfx[] = [
  ...titleSfx,
  // golpes de cambio de bloque
  {src: 'sfx/hit.wav', at: ws(7), vol: 0.22, dur: 1.2},
  {src: 'sfx/whoosh_trans.wav', at: ws(7) - 0.08, vol: 0.3},
  {src: 'sfx/pop.wav', at: ws(15), vol: 0.28},
  // tachado precios/producto
  {src: 'sfx/whoosh_d.wav', at: SCENES.tachado.start - 0.05, vol: 0.25, dur: 0.9},
  {src: 'sfx/strike.wav', at: SCENES.tachado.strike1, vol: 1.0, dur: 0.55},
  {src: 'sfx/strike.wav', at: SCENES.tachado.strike2, vol: 1.0, dur: 0.55, trim: 0.6},
  // riser hacia "es otro"
  {src: 'sfx/riser.wav', at: ws(35) - 3.6, vol: 0.32, dur: 3.6},
  {src: 'sfx/hit.wav', at: ws(35), vol: 0.3, dur: 1.2},
  // personas / compra online
  {src: 'sfx/whoosh_long.wav', at: ws(37) - 0.15, vol: 0.25, dur: 1.2},
  {src: 'sfx/whoosh_trans.wav', at: ws(43) - 0.05, vol: 0.32},
  // móvil
  {src: 'sfx/flash.wav', at: SCENES.movil.start, vol: 0.22, dur: 0.8},
  {src: 'sfx/whoosh_rocks.wav', at: SCENES.movil.start - 0.1, vol: 0.22, dur: 1.4},
  {src: 'sfx/pop.wav', at: ws(53), vol: 0.22},
  // HUD + segundos
  {src: 'sfx/digital.wav', at: SCENES.hud.start, vol: 0.3, dur: 1.2, trim: 0.5},
  {src: 'sfx/reloj.wav', at: ws(58), vol: 0.5, dur: 2.0},
  {src: 'sfx/click.wav', at: SCENES.hud.confiar, vol: 0.6},
  {src: 'sfx/hit.wav', at: SCENES.hud.noConfiar, vol: 0.28, dur: 1.0},
  // CONFIANZA
  {src: 'sfx/flash.wav', at: SCENES.confianza.start, vol: 0.2, dur: 0.8},
  {src: 'sfx/hit.wav', at: SCENES.confianza.start, vol: 0.22, dur: 1.0},
  {src: 'sfx/typing.wav', at: SCENES.confianza.noteStart, vol: 0.55, dur: 2.9, trim: 1.0},
  {src: 'sfx/hit.wav', at: SCENES.confianza.t1, vol: 0.25, dur: 1.0},
  {src: 'sfx/hit.wav', at: SCENES.confianza.t2, vol: 0.25, dur: 1.0},
  // perdiste la venta
  {src: 'sfx/boom.wav', at: ws(79), vol: 0.26, dur: 2.0},
  // collage
  {src: 'sfx/whoosh_long.wav', at: SCENES.collage.start - 0.12, vol: 0.28, dur: 1.2},
  // te compra / no te compra
  {src: 'sfx/whoosh_d.wav', at: ws(104) - 0.08, vol: 0.25, dur: 0.9},
  {src: 'sfx/cash.wav', at: ws(108), vol: 0.45},
  {src: 'sfx/hit.wav', at: ws(112), vol: 0.3, dur: 1.2},
  // perdiendo ventas
  {src: 'sfx/whoosh_long.wav', at: ws(118) - 0.12, vol: 0.25, dur: 1.2},
  // ayudemos / AYUDA
  {src: 'sfx/flash.wav', at: ws(127), vol: 0.22, dur: 0.8},
  {src: 'sfx/riser.wav', at: ws(137) - 2.2, vol: 0.28, dur: 2.2, trim: 1.4},
  {src: 'sfx/hit.wav', at: ws(137), vol: 0.32, dur: 1.4},
  {src: 'sfx/tecla.wav', at: SCENES.comentario.typeAt + 0.0, vol: 0.7},
  {src: 'sfx/tecla.wav', at: SCENES.comentario.typeAt + 0.09, vol: 0.7},
  {src: 'sfx/tecla.wav', at: SCENES.comentario.typeAt + 0.18, vol: 0.7},
  {src: 'sfx/tecla.wav', at: SCENES.comentario.typeAt + 0.27, vol: 0.7},
  {src: 'sfx/tecla.wav', at: SCENES.comentario.typeAt + 0.36, vol: 0.7},
  // cierre
  {src: 'sfx/whoosh_long.wav', at: ws(138) - 0.12, vol: 0.28, dur: 1.2},
  {src: 'sfx/hit.wav', at: ws(138), vol: 0.3, dur: 1.4},
];
