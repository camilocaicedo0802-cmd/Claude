// Ganador 2 · «Publicar no es hacer marketing» — PROPUESTA C «Escritorio digital».
// La persona alterna entre pantalla completa y una ventana sobre un escritorio; a su alrededor
// se abren ventanas de apps (publicar, nota, saldo, estadísticas, perfil, monitor de ventas…),
// un cursor hace clic y los subtítulos son de tipo karaoke en una píldora.
import {wordTimes} from '../engine/helpers';
import {Sfx, Spec} from '../engine/types';
import {FACES} from './faces';
import {SEGMENTS, SPEECH_FRAMES, WORDS} from './timeline';

export const {ws, we} = wordTimes(WORDS);
export const SPEECH = SPEECH_FRAMES / 30;
export const TOTAL = SPEECH + 2.7;
const segStart = (i: number) => SEGMENTS[i].start / 30;

// ---------- escenas (s) ----------
export const T = {
  win1: ws(3) - 0.06, // «publicar» → ventana + app de publicar
  full1: segStart(1), // «Y lo más triste…»
  win2: segStart(3), // «Es tener redes sociales…» → estadísticas
  full2: segStart(5), // «¿Y sabe qué significa eso?»
  win3: ws(44) - 0.06, // «Que tu contenido…» → perfil
  full3: segStart(6), // «Pero lo peor…»
  close: ws(72), // «Pero quiero decirte algo» → se cierran las ventanas
  win4: segStart(10), // «lo que no genera venta» → monitor
  off: ws(86) + 0.1, // «muerto» → se apaga la pantalla
  on: ws(94), // «reviva» → desfibrilador
  end: SPEECH,
};

/** Modos de la pantalla de la persona: completa, ventana abajo a la derecha, cierre. */
export type ScreenState = {x: number; y: number; k: number};
export const FULL: ScreenState = {x: 0, y: 0, k: 1};
export const WIN: ScreenState = {x: 400, y: 740, k: 0.6};
export const ENDW: ScreenState = {x: 270, y: 860, k: 0.5};
export const MODES: {t: number; s: ScreenState}[] = [
  {t: 0, s: FULL},
  {t: T.win1, s: WIN},
  {t: T.full1, s: FULL},
  {t: T.win2, s: WIN},
  {t: T.full2, s: FULL},
  {t: T.win3, s: WIN},
  {t: T.full3, s: FULL},
  {t: T.win4, s: WIN},
  {t: T.on + 0.25, s: FULL},
  {t: T.end, s: ENDW},
];

/** Palabras que se encienden en morado en el subtítulo karaoke. */
export const KEY = new Set([3, 11, 15, 24, 26, 29, 30, 38, 42, 50, 53, 63, 71, 77, 82, 86, 94, 98]);

/** Zooms de golpe (solo a pantalla completa). */
export const SNAPS: {t: number; f: number}[] = [
  {t: ws(15), f: 1.1},
  {t: ws(42), f: 1.12},
  {t: ws(53), f: 1.08},
  {t: ws(74), f: 1.12},
  {t: ws(98), f: 1.08},
];

/** Cursor: posiciones (px) y clics. */
export const CURSOR: {t: number; x: number; y: number; click?: boolean}[] = [
  {t: ws(3) + 0.25, x: 980, y: 520},
  {t: ws(7) - 0.04, x: 470, y: 805},
  {t: ws(7) + 0.02, x: 470, y: 805, click: true},
  {t: ws(8) - 0.05, x: 600, y: 690},
  {t: ws(73), x: 900, y: 600},
  {t: ws(74) + 0.05, x: 82, y: 133},
  {t: ws(74) + 0.11, x: 82, y: 133, click: true},
  {t: ws(75) + 0.15, x: 260, y: 620},
  {t: ws(97), x: 980, y: 520},
  {t: ws(98) + 0.3, x: 968, y: 240},
  {t: ws(98) + 0.36, x: 968, y: 240, click: true},
  {t: SPEECH - 0.02, x: 1020, y: 420},
];
export const CURSOR_ON: [number, number][] = [
  [ws(3) + 0.25, ws(8) + 0.2],
  [ws(73), ws(75) + 0.3],
  [ws(97), SPEECH],
];

export const SHAKES = [ws(11) + 0.05, ws(38), ws(50), T.on];

// ---------- spec del motor (sonido, segmentos, caras) ----------
export const SPEC_C: Spec = {
  id: 'v3',
  clipPrefix: 'v3',
  segments: SEGMENTS,
  words: WORDS,
  faces: FACES,
  framing: {
    0: {scale: [1.0, 1.0]},
    1: {scale: [1.04, 1.08]},
    2: {scale: [1.0, 1.04]},
    3: {scale: [1.0, 1.0]},
    4: {scale: [1.0, 1.0]},
    5: {scale: [1.0, 1.03]},
    6: {scale: [1.06, 1.1]},
    7: {scale: [1.0, 1.04]},
    8: {scale: [1.1, 1.14]},
    9: {scale: [1.16, 1.2]},
    10: {scale: [1.0, 1.0]},
    11: {scale: [1.0, 1.0]},
    12: {scale: [1.0, 1.06]},
    13: {scale: [1.06, 1.1]},
    14: {scale: [1.12, 1.14]},
  },
  titles: [],
  noSubs: [[T.end, 999]],
  broll: [],
  cards: [],
  defocus: [],
  flashes: [],
  whips: [],
  pulses: [],
  // corte en seco de la música en «Pero quiero decirte algo» (como el corte de la referencia)
  music: {src: 'music/v3_403.wav', volume: 0.09, stopFrom: T.close - 0.03, stopTo: T.win4, fadeOutAt: TOTAL - 1.0},
  sfx: [],
  total: TOTAL,
};

// ---------- efectos de sonido (banco de la referencia + paquete del cliente) ----------
const typing = (from: number, to: number, vol = 0.32): Sfx[] => {
  const out: Sfx[] = [];
  for (let t = from; t < to; t += 0.42) out.push({src: 'sfx/teclado.wav', at: t, vol, dur: 0.45});
  return out;
};
SPEC_C.sfx = [
  // encendido
  {src: 'sfx/whoosh_b.wav', at: 0, vol: 0.22, dur: 0.6},
  // publicar
  {src: 'sfx/whoosh_a.wav', at: T.win1 - 0.1, vol: 0.28, dur: 0.7},
  {src: 'sfx/pop.wav', at: T.win1 + 0.12, vol: 0.24},
  ...typing(ws(3) + 0.3, ws(7) - 0.15, 0.26),
  {src: 'sfx/mouse.wav', at: ws(7) + 0.02, vol: 0.8},
  {src: 'sfx/notif.wav', at: ws(7) + 0.12, vol: 0.4},
  {src: 'sfx/pop.wav', at: ws(8), vol: 0.24},
  ...typing(ws(8) + 0.05, ws(11) - 0.05, 0.22),
  {src: 'sfx/error.wav', at: ws(11) + 0.05, vol: 0.32, dur: 1.2},
  // triste / pérdida de dinero
  {src: 'sfx/whoosh_b.wav', at: T.full1 - 0.1, vol: 0.26, dur: 0.7},
  {src: 'sfx/pop.wav', at: ws(22), vol: 0.22},
  {src: 'sfx/pop.wav', at: ws(24) - 0.02, vol: 0.24},
  {src: 'sfx/contador.wav', at: ws(24) + 0.05, vol: 0.2, dur: 1.0},
  {src: 'sfx/hit.wav', at: ws(26) + 0.25, vol: 0.24, dur: 1.0},
  // estadísticas
  {src: 'sfx/whoosh_d.wav', at: T.win2 - 0.1, vol: 0.28, dur: 0.8},
  {src: 'sfx/digital.wav', at: ws(28), vol: 0.2, dur: 0.6},
  {src: 'sfx/boom.wav', at: ws(38), vol: 0.3, dur: 1.4},
  // significa / perfil
  {src: 'sfx/whoosh_c.wav', at: T.full2 - 0.1, vol: 0.24, dur: 0.6},
  {src: 'sfx/whoosh_a.wav', at: T.win3 - 0.1, vol: 0.26, dur: 0.7},
  {src: 'sfx/pop.wav', at: ws(46), vol: 0.24},
  {src: 'sfx/error.wav', at: ws(50), vol: 0.34, dur: 1.2},
  // lo peor / nivel
  {src: 'sfx/whoosh_b.wav', at: T.full3 - 0.1, vol: 0.24, dur: 0.6},
  {src: 'sfx/pop.wav', at: ws(62), vol: 0.24},
  {src: 'sfx/pop.wav', at: ws(62) + 0.12, vol: 0.2},
  {src: 'sfx/pop.wav', at: ws(62) + 0.24, vol: 0.2},
  {src: 'sfx/pop.wav', at: ws(62) + 0.36, vol: 0.2},
  {src: 'sfx/pop.wav', at: ws(62) + 0.48, vol: 0.24},
  {src: 'sfx/whoosh_a.wav', at: ws(67) - 0.1, vol: 0.24, dur: 0.6},
  {src: 'sfx/riser.wav', at: ws(70) - 0.7, vol: 0.22, dur: 0.8, trim: 2.8},
  {src: 'sfx/hit.wav', at: ws(71), vol: 0.26, dur: 1.0},
  // cierre de ventanas (la música se corta)
  {src: 'sfx/mouse.wav', at: ws(74) + 0.11, vol: 0.8},
  {src: 'sfx/whoosh_c.wav', at: ws(74) + 0.12, vol: 0.24, dur: 0.6},
  // monitor de ventas
  {src: 'sfx/whoosh_d.wav', at: T.win4 - 0.1, vol: 0.26, dur: 0.8},
  {src: 'sfx/beep.wav', at: ws(79), vol: 0.5},
  {src: 'sfx/beep.wav', at: ws(82) - 0.05, vol: 0.4},
  {src: 'sfx/beep.wav', at: ws(84), vol: 0.3},
  {src: 'sfx/flatline.wav', at: ws(86), vol: 0.42, dur: 1.8},
  {src: 'sfx/apagar.wav', at: T.off, vol: 0.4, dur: 1.4},
  // desfibrilador + revivir
  {src: 'sfx/riser.wav', at: T.on - 1.2, vol: 0.22, dur: 1.2, trim: 2.4},
  {src: 'sfx/boom.wav', at: T.on, vol: 0.38, dur: 1.6},
  {src: 'sfx/flash.wav', at: T.on, vol: 0.3, dur: 0.8},
  {src: 'sfx/beep.wav', at: T.on + 0.3, vol: 0.5},
  {src: 'sfx/beep.wav', at: T.on + 0.72, vol: 0.5},
  {src: 'sfx/beep.wav', at: T.on + 1.14, vol: 0.45},
  ...typing(ws(97), ws(98) + 0.25, 0.3),
  {src: 'sfx/mouse.wav', at: ws(98) + 0.36, vol: 0.8},
  {src: 'sfx/notif.wav', at: ws(98) + 0.45, vol: 0.42},
  // cierre
  {src: 'sfx/whoosh_trans.wav', at: T.end - 0.1, vol: 0.28},
  {src: 'sfx/pop.wav', at: T.end + 0.45, vol: 0.26},
  ...typing(T.end + 0.8, T.end + 1.5, 0.26),
  {src: 'sfx/hit.wav', at: T.end + 1.6, vol: 0.22, dur: 1.0},
];
void we;
void segStart;
