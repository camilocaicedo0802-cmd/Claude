// Ganador 1 · «Hay 2 tipos de redes» — PROPUESTA B «Pop cinético».
// Misma voz y cortes que v9; cambia toda la edición: subtítulos cinéticos grandes, fondo sustituido
// (persona recortada), pantalla dividida, burbuja con la cara y motion graphics a pantalla completa.
import {wordTimes} from '../engine/helpers';
import {Sfx, Spec} from '../engine/types';
import {FACES} from '../v9/faces';
import {SEGMENTS, SPEECH_FRAMES, WORDS} from '../v9/timeline';
import {CHUNKS} from './chunks';

export const {ws, we} = wordTimes(WORDS);
export const SPEECH = SPEECH_FRAMES / 30;
export const TOTAL = SPEECH + 2.4;
const segStart = (i: number) => SEGMENTS[i].start / 30;

// ---------- modos de pantalla (s) ----------
export const T = {
  s1: segStart(1), // fondo morado + «2» gigante
  s2: segStart(2), // versus a pantalla completa + burbuja
  s3: segStart(4), // sala (la burbuja se expande)
  s4: segStart(5), // fondo calendario
  s5: segStart(7), // sala + batería
  s6: ws(47) - 0.03, // chat + burbuja
  s7: segStart(8), // fondo «sí venden»
  s8: segStart(9), // sala
  s9: segStart(10), // pantalla dividida con B-roll
  s10: segStart(11), // visor de cámara + polaroids
  s11: segStart(12), // embudo + anuncio + burbuja
  s12: segStart(13), // foco
  s13: segStart(14), // botones A/B
  end: SPEECH, // cierre
};

/** Palabras que se resaltan en el subtítulo (recuadro morado). */
export const KEY = new Set([5, 6, 8, 9, 12, 17, 23, 28, 34, 35, 45, 46, 57, 59, 63, 64, 69, 73, 75, 81, 85, 89, 90, 96, 98, 100, 101, 106, 115, 119, 120]);
/** Texto mostrado para alguna palabra concreta. */
export const DISPLAY: Record<number, string> = {5: '2'};

/** Zooms de golpe (factor extra hasta el final del segmento). */
export const SNAPS: {t: number; f: number}[] = [
  {t: ws(5), f: 1.1},
  {t: ws(23), f: 1.08},
  {t: ws(45), f: 1.1},
  {t: ws(69), f: 1.14},
  {t: ws(90), f: 1.08},
  {t: ws(106), f: 1.08},
  {t: ws(115), f: 1.07},
];

/** Tramos sin subtítulo (el gráfico ya cuenta lo que dice). */
export const NO_CAPS: [number, number][] = [
  [T.s2, T.s3 - 0.02],
  [T.s6, T.s7],
  [T.end, 999],
];

/** Altura del subtítulo según el modo. */
export const capY = (t: number) => (t >= T.s9 && t < T.s10 ? 960 : t >= T.s11 && t < T.s12 ? 1290 : 1450);

export const SHAKES = [ws(5), T.s7, ws(102), ws(120) + 0.12];

// ---------- spec para el motor (sonido, segmentos, caras) ----------
export const SPEC_B: Spec = {
  id: 'v9b',
  clipPrefix: 'v9',
  segments: SEGMENTS,
  words: WORDS,
  faces: FACES,
  framing: {
    0: {scale: [1.0, 1.02]},
    1: {scale: [1.0, 1.04]},
    2: {scale: [1, 1]},
    3: {scale: [1, 1]},
    4: {scale: [1.16, 1.18]},
    5: {scale: [1.0, 1.02]},
    6: {scale: [1.02, 1.06]},
    7: {scale: [1.1, 1.13]},
    8: {scale: [1.04, 1.08]},
    9: {scale: [1.0, 1.03]},
    10: {scale: [1, 1]},
    11: {scale: [1.0, 1.12]},
    12: {scale: [1.0, 1.0]},
    13: {scale: [1.0, 1.12]},
    14: {scale: [1.0, 1.04]},
    15: {scale: [1.14, 1.16]},
    16: {scale: [1.2, 1.22]},
  },
  titles: [],
  noSubs: NO_CAPS,
  broll: [],
  cards: [],
  defocus: [],
  flashes: [],
  whips: [],
  pulses: [],
  music: {src: 'music/v9_lilpump.wav', volume: 0.085, fadeOutAt: TOTAL - 0.9},
  sfx: [],
  total: TOTAL,
};

// ---------- efectos de sonido (mismo banco que la referencia) ----------
const sfx: Sfx[] = [
  // gancho
  {src: 'sfx/whoosh_trans.wav', at: T.s1 - 0.12, vol: 0.32},
  {src: 'sfx/boom.wav', at: ws(5), vol: 0.32, dur: 1.6},
  {src: 'sfx/whoosh_b.wav', at: ws(8) - 0.05, vol: 0.18, dur: 0.7},
  // versus
  {src: 'sfx/whoosh_a.wav', at: T.s2 - 0.1, vol: 0.3, dur: 0.8},
  {src: 'sfx/pop.wav', at: ws(12), vol: 0.26},
  {src: 'sfx/pop.wav', at: ws(12) + 0.17, vol: 0.22},
  {src: 'sfx/cash.wav', at: ws(12) + 0.3, vol: 0.4},
  {src: 'sfx/strike.wav', at: ws(16), vol: 0.26, dur: 1.0},
  {src: 'sfx/whoosh_long.wav', at: T.s3 - 0.22, vol: 0.28, dur: 1.2},
  // diferencia
  // calendario
  {src: 'sfx/digital.wav', at: T.s4 - 0.03, vol: 0.3, dur: 0.6},
  {src: 'sfx/reloj.wav', at: ws(29), vol: 0.22, dur: 2.2},
  {src: 'sfx/hit.wav', at: ws(35), vol: 0.24, dur: 1.0},
  // batería
  {src: 'sfx/flash.wav', at: T.s5 - 0.03, vol: 0.2, dur: 0.6},
  {src: 'sfx/pop.wav', at: T.s5 + 0.05, vol: 0.26},
  {src: 'sfx/digital8bit.wav', at: ws(45), vol: 0.24, dur: 0.9},
  // chat
  {src: 'sfx/whoosh_b.wav', at: T.s6 - 0.1, vol: 0.3, dur: 0.8},
  {src: 'sfx/pop.wav', at: ws(49), vol: 0.22},
  {src: 'sfx/pop.wav', at: ws(54), vol: 0.26},
  {src: 'sfx/pop.wav', at: ws(57), vol: 0.26},
  {src: 'sfx/pop.wav', at: ws(59), vol: 0.26},
  // sí venden
  {src: 'sfx/whoosh_trans.wav', at: T.s7 - 0.14, vol: 0.32},
  {src: 'sfx/hit.wav', at: T.s7, vol: 0.3, dur: 1.2},
  {src: 'sfx/cash.wav', at: ws(64), vol: 0.42},
  // pantalla dividida
  {src: 'sfx/whoosh_d.wav', at: T.s9 - 0.1, vol: 0.3, dur: 0.9},
  {src: 'sfx/whoosh_a.wav', at: ws(81) - 0.12, vol: 0.22, dur: 0.7},
  {src: 'sfx/whoosh_c.wav', at: ws(83) - 0.12, vol: 0.22, dur: 0.7},
  {src: 'sfx/whoosh_d.wav', at: T.s10 - 0.1, vol: 0.26, dur: 0.9},
  // fotos
  {src: 'sfx/flash.wav', at: ws(89), vol: 0.45, dur: 1.0},
  {src: 'sfx/flash.wav', at: ws(90) + 0.22, vol: 0.4, dur: 1.0},
  // embudo + anuncio
  {src: 'sfx/riser.wav', at: T.s11 - 1.0, vol: 0.18, dur: 1.0, trim: 2.6},
  {src: 'sfx/whoosh_long.wav', at: T.s11 - 0.1, vol: 0.26, dur: 1.2},
  {src: 'sfx/tecla.wav', at: ws(96), vol: 0.22, dur: 1.0},
  {src: 'sfx/whoosh_a.wav', at: ws(99) - 0.1, vol: 0.24, dur: 0.7},
  {src: 'sfx/click.wav', at: ws(101) + 0.05, vol: 0.6},
  {src: 'sfx/cash.wav', at: ws(101) + 0.12, vol: 0.42},
  // pregunta
  {src: 'sfx/flash.wav', at: T.s12 - 0.03, vol: 0.22, dur: 0.6},
  {src: 'sfx/boom.wav', at: ws(102), vol: 0.26, dur: 1.6},
  // botones A/B
  {src: 'sfx/digital.wav', at: T.s13 - 0.03, vol: 0.26, dur: 0.6},
  {src: 'sfx/pop.wav', at: ws(108), vol: 0.22},
  {src: 'sfx/pop.wav', at: ws(114), vol: 0.26},
  {src: 'sfx/pop.wav', at: ws(119), vol: 0.28},
  {src: 'sfx/click.wav', at: ws(120) + 0.12, vol: 0.6},
  {src: 'sfx/cash.wav', at: ws(120) + 0.16, vol: 0.38},
  // cierre
  {src: 'sfx/whoosh_trans.wav', at: T.end - 0.14, vol: 0.3},
  {src: 'sfx/typing.wav', at: T.end + 0.45, vol: 0.3, dur: 0.6},
  {src: 'sfx/pop.wav', at: T.end + 1.05, vol: 0.3},
];
// Subtítulos (referencia §8): cada palabra clave que entra = whoosh corto (−12 dB respecto a la voz),
// nunca dos efectos en menos de 0,35 s ni dos whooshes de subtítulo en menos de 0,5 s.
const capSfx: Sfx[] = [];
const WH = ['sfx/whoosh_a.wav', 'sfx/whoosh_b.wav', 'sfx/whoosh_c.wav'];
for (const c of CHUNKS) {
  const i = c.idx.find((x) => KEY.has(x));
  if (i === undefined) continue;
  const at = ws(i) - 0.04;
  if (NO_CAPS.some(([a, b]) => at >= a && at < b)) continue;
  if (sfx.some((s) => Math.abs(s.at - at) < 0.35)) continue;
  if (capSfx.length && at - capSfx[capSfx.length - 1].at < 0.5) continue;
  capSfx.push({src: WH[capSfx.length % 3], at, vol: 0.2, dur: 0.7});
}
SPEC_B.sfx = [...sfx, ...capSfx];
export const CAP_SFX = capSfx.length;
void we;
