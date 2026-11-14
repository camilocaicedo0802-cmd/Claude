// Ganador 3 · «Te tengo una buena noticia» + Grow Marketing — PROPUESTA D «Collage».
// Papel con grano, fotos y B-roll en marcos rasgados con cinta, garabatos de rotulador que se dibujan,
// sellos, movimiento stop-motion y transiciones de hoja de papel. Textos dinámicos como la referencia (§10.9).
import {wordTimes} from '../engine/helpers';
import {Sfx, Spec, TitleDef, TitleLine, TitleWord} from '../engine/types';
import {FACES} from './faces';
import {SEGMENTS, SPEECH_FRAMES, WORDS} from './timeline';

export const {ws, we} = wordTimes(WORDS);
export const SPEECH = SPEECH_FRAMES / 30;
export const TOTAL = SPEECH + 2.8;
const segStart = (i: number) => SEGMENTS[i].start / 30;

// ---------- cortes de escena ----------
export const T = {
  c1: segStart(1), // → foto (no vendes)
  c2: segStart(4), // → completa (no es que no funcionen)
  c3: segStart(6), // → recorte (realidad)
  c4: segStart(8), // → foto (el cliente…)
  c5: segStart(14), // → completa (te escribe)
  c6: segStart(16), // → foto (ocupados / todólogo)
  c7: segStart(19), // → completa (escucha)
  c8: segStart(22), // → recorte (Grow Marketing)
  c9: segStart(23), // → foto (grabamos / fotos)
  c10: segStart(25), // → completa (100 %)
  end: SPEECH,
};

export type Foto = {cx: number; cy: number; k: number; rot: number};
export type Modo = {t: number; mode: 'full' | 'foto' | 'recorte' | 'end'; foto?: Foto};
export const MODOS: Modo[] = [
  {t: 0, mode: 'full'},
  {t: T.c1, mode: 'foto', foto: {cx: 560, cy: 1080, k: 0.58, rot: -3}},
  {t: T.c2, mode: 'full'},
  {t: T.c3, mode: 'recorte'},
  {t: T.c4, mode: 'foto', foto: {cx: 700, cy: 1300, k: 0.5, rot: 3}},
  {t: T.c5, mode: 'full'},
  {t: T.c6, mode: 'foto', foto: {cx: 540, cy: 1430, k: 0.46, rot: -2}},
  {t: T.c7, mode: 'full'},
  {t: T.c8, mode: 'recorte'},
  {t: T.c9, mode: 'foto', foto: {cx: 760, cy: 1380, k: 0.5, rot: -3}},
  {t: T.c10, mode: 'full'},
  {t: T.end, mode: 'end'},
];
export const modoAt = (t: number) => [...MODOS].reverse().find((m) => t >= m.t)!;

/** Transiciones: hoja de papel (arriba) o destello + caída stop-motion. */
export const HOJAS: {t: number; dir: 'up' | 'left'}[] = [
  {t: 0, dir: 'up'},
  {t: T.c1, dir: 'up'},
  {t: T.c3, dir: 'left'},
  {t: T.c5, dir: 'up'},
  {t: T.c7, dir: 'left'},
  {t: T.c9, dir: 'up'},
  {t: T.end, dir: 'left'},
];
export const DESTELLOS = [T.c2, T.c4, T.c6, T.c8, T.c10, ws(156)];

/** Zooms de golpe (solo a pantalla completa). */
export const SNAPS: {t: number; f: number}[] = [
  {t: ws(29), f: 1.08},
  {t: ws(38), f: 1.1},
  {t: ws(89), f: 1.1},
  {t: ws(127), f: 1.08},
  {t: ws(165), f: 1.1},
];
export const SHAKES = [ws(48), ws(67), ws(89), ws(112), ws(165)];

// ---------- spec del motor ----------
export const SPEC_D: Spec = {
  id: 'v8',
  clipPrefix: 'v8',
  segments: SEGMENTS,
  words: WORDS,
  faces: FACES,
  framing: {
    0: {scale: [1.0, 1.04]},
    4: {scale: [1.0, 1.03]},
    5: {scale: [1.08, 1.12]},
    6: {scale: [1, 1]},
    7: {scale: [1, 1]},
    14: {scale: [1.0, 1.03]},
    15: {scale: [1.04, 1.1]},
    19: {scale: [1.1, 1.12]},
    20: {scale: [1.0, 1.02]},
    21: {scale: [1.02, 1.08]},
    22: {scale: [1, 1]},
    25: {scale: [1.06, 1.08]},
    26: {scale: [1.1, 1.12]},
    27: {scale: [1.04, 1.08]},
  },
  titles: [],
  noSubs: [[T.end, 999]],
  broll: [],
  cards: [],
  defocus: [],
  flashes: [],
  whips: [],
  pulses: [],
  music: {src: 'music/v8_399.wav', volume: 0.085, fadeOutAt: TOTAL - 1.0},
  sfx: [],
  total: TOTAL,
};

// ---------- textos dinámicos (§10.9), letras lisas ----------
const tw = (i: number, text?: string): TitleWord => ({text: text ?? WORDS[i].text.replace(/[,.]/g, '').toLowerCase(), at: ws(i)});
const L = (idx: number[], color: TitleLine['color'], size: number, extra: Partial<TitleLine> = {}): TitleLine => ({words: idx.map((i) => tw(i)), color, size, ...extra});
const P = {plain: true} as const;
const r = (a: number, b: number) => Array.from({length: b - a + 1}, (_, i) => a + i);

export const TITLES: TitleDef[] = [
  {...P, id: 'buena', start: ws(0) - 0.02, end: T.c1 - 0.06, y: 'head', overlap: 80, scene: true, covers: r(0, 4),
    lines: [L([0, 1, 2], 'white', 84, {dx: -40}), L([3, 4], 'purple', 120, {dx: 40})]},
  {...P, id: 'novendes', start: ws(5) - 0.02, end: ws(12) - 0.04, y: 1770, covers: r(5, 11),
    lines: [L([5, 6, 7, 8], 'white', 64, {dx: -30}), L([9, 10, 11], 'purple', 96, {dx: 40})]},
  {...P, id: 'interesar', start: ws(12) - 0.02, end: T.c2 - 0.06, y: 1765, covers: r(12, 21),
    lines: [L(r(12, 17), 'white', 56, {dx: -40}), L([18, 19, 20], 'white', 66, {dx: 30}), L([21], 'purple', 150, {upper: true, dx: -10})]},
  {...P, id: 'funcionen', start: T.c2 + 0.08, end: ws(30) - 0.04, y: 430, scene: true, covers: r(22, 29),
    lines: [L(r(22, 27), 'white', 60, {dx: -30}), L([28, 29], 'purple', 130, {dx: 40})]},
  {...P, id: 'mala', start: ws(30) - 0.02, end: T.c3 - 0.06, y: 1600, covers: r(30, 39),
    lines: [L(r(30, 34), 'white', 64, {dx: -40}), L([35], 'purple', 150, {dx: 30}), L(r(36, 39), 'white', 84, {dx: 60})]},
  {...P, id: 'realidad', start: T.c3 + 0.05, end: ws(48) - 0.04, y: 1620, covers: r(40, 47),
    lines: [L([40, 41, 42], 'white', 70, {dx: -40}), L([43], 'purple', 160, {dx: 30}), L(r(44, 47), 'white', 64, {dx: 60})]},
  {...P, id: 'cliente', start: T.c4 + 0.05, end: ws(58) - 0.04, y: 1640, covers: r(49, 57),
    lines: [L(r(49, 53), 'white', 64, {dx: -30}), L(r(54, 57), 'purple', 100, {dx: 40})]},
  {...P, id: 'nolegusta', start: ws(58) - 0.02, end: ws(70) - 0.04, y: 1640, covers: r(58, 69),
    lines: [L(r(58, 66), 'white', 56, {dx: -30}), L([67, 68, 69], 'purple', 120, {upper: true, dx: 30})]},
  {...P, id: 'siguiente', start: ws(70) - 0.02, end: T.c5 - 0.06, y: 1640, covers: r(70, 75),
    lines: [L([70], 'white', 80, {dx: -30}), L([71, 72, 73], 'white', 64, {dx: 40}), L([74], 'purple', 140, {dx: -10}), L([75], 'white', 90, {dx: 60})]},
  {...P, id: 'escribe', start: T.c5 + 0.05, end: ws(84) - 0.04, y: 1600, covers: r(76, 83),
    lines: [L(r(76, 79), 'white', 64, {dx: -40}), L([80, 81], 'white', 70, {dx: 20}), L([82, 83], 'purple', 140, {dx: 40})]},
  {...P, id: 'contestas', start: ws(84) - 0.02, end: T.c6 - 0.06, y: 1600, covers: r(84, 89),
    lines: [L(r(84, 88), 'white', 70, {dx: -40}), L([89], 'purple', 150, {upper: true, dx: 30})]},
  {...P, id: 'clientes', start: T.c6 + 0.05, end: ws(98) - 0.04, y: 1760, covers: r(90, 97),
    lines: [L(r(90, 93), 'white', 60, {dx: -30}), L(r(94, 97), 'purple', 76, {dx: 40})]},
  {...P, id: 'ocupados', start: ws(98) - 0.02, end: ws(105) - 0.04, y: 1740, covers: r(98, 104),
    lines: [L([98], 'white', 70, {dx: -40}), L([99], 'purple', 160, {upper: true, dx: 20}), L(r(100, 104), 'white', 60, {dx: 60})]},
  {...P, id: 'despachando', start: ws(105) - 0.02, end: ws(110) - 0.04, y: 1760, covers: r(105, 109),
    lines: [L(r(105, 108), 'white', 60, {dx: -30}), L([109], 'purple', 130, {dx: 40})]},
  {...P, id: 'todologo', start: ws(110) - 0.02, end: T.c7 - 0.06, y: 1740, covers: r(110, 115),
    lines: [L([110, 111], 'white', 70, {dx: -40}), L([112], 'purple', 170, {upper: true, dx: 20}), L([113, 114, 115], 'white', 64, {dx: 60})]},
  {...P, id: 'escucha', start: T.c7 + 0.05, end: ws(117) - 0.04, y: 'head', overlap: 60, scene: true, covers: [116],
    lines: [{words: [tw(116, 'escucha')], color: 'purple', size: 190, upper: true}]},
  {...P, id: 'equipo', start: ws(117) - 0.02, end: ws(128) - 0.04, y: 1600, covers: r(117, 127),
    lines: [L(r(117, 123), 'white', 56, {dx: -40}), L([124, 125, 126], 'white', 76, {dx: 20}), L([127], 'purple', 160, {dx: 40})]},
  {...P, id: 'porti', start: ws(128) - 0.02, end: T.c8 - 0.06, y: 1600, covers: r(128, 131),
    lines: [L([128, 129], 'white', 84, {dx: -40}), L([130, 131], 'purple', 180, {upper: true, dx: 30})]},
  {...P, id: 'grow', start: T.c8 + 0.05, end: ws(138) - 0.04, y: 1610, covers: r(132, 137),
    lines: [L(r(132, 135), 'white', 60, {dx: -40}), {words: [tw(136, 'grow')], color: 'purple', size: 170, upper: true, dx: 20}, {words: [tw(137, 'marketing')], color: 'white', size: 110, upper: true, dx: 60}]},
  {...P, id: 'expertos', start: ws(138) - 0.02, end: ws(143) - 0.04, y: 1610, covers: r(138, 142),
    lines: [L([138], 'white', 80, {dx: -40}), L([139], 'purple', 160, {dx: 30}), L(r(140, 142), 'white', 64, {dx: 60})]},
  {...P, id: 'estrategia', start: ws(143) - 0.02, end: ws(145) - 0.04, y: 1610, covers: [143, 144],
    lines: [L([143], 'white', 80, {dx: -40}), L([144], 'purple', 140, {upper: true, dx: 20})]},
  {...P, id: 'vamos', start: ws(145) - 0.02, end: T.c9 - 0.06, y: 1610, covers: r(145, 150),
    lines: [L(r(145, 147), 'white', 64, {dx: -30}), L(r(148, 150), 'purple', 120, {dx: 40})]},
  {...P, id: 'contenido', start: T.c9 + 0.05, end: ws(155) - 0.04, y: 1720, covers: r(151, 154),
    lines: [L([151], 'white', 76, {dx: -40}), L([152], 'purple', 150, {upper: true, dx: 20}), L([153, 154], 'white', 70, {dx: 60})]},
  {...P, id: 'fotos', start: ws(155) - 0.02, end: ws(158) - 0.04, y: 1720, covers: r(155, 157),
    lines: [L([155, 156], 'white', 76, {dx: -30}), L([157], 'purple', 130, {dx: 40})]},
  {...P, id: 'importante', start: ws(158) - 0.02, end: T.c10 - 0.06, y: 1720, covers: r(158, 163),
    lines: [L(r(158, 160), 'white', 64, {dx: -40}), L([161], 'purple', 140, {upper: true, dx: 20}), L([162, 163], 'white', 64, {dx: 60})]},
  {...P, id: 'cien', start: T.c10 + 0.05, end: T.end, y: 1600, covers: r(164, 171),
    lines: [L([164], 'white', 84, {dx: -40}), {words: [tw(165, '100%')], color: 'purple', size: 210, upper: true, dx: 20}, L([167], 'white', 110, {dx: 40}), L(r(168, 171), 'white', 60, {dx: 60})]},
];
SPEC_D.titles = TITLES;

// ---------- efectos de sonido ----------
const ROT = (n: number) => ({src: 'sfx/rotulador.wav', trim: [0, 1.24, 2.76][n % 3], dur: 0.9, vol: 0.5});
const sfx: Sfx[] = [
  // transiciones de papel
  ...HOJAS.map((h) => ({src: 'sfx/rasgar.wav', at: Math.max(0, h.t - 0.12), vol: 0.5, dur: 0.6})),
  ...HOJAS.filter((h) => h.t > 0).map((h) => ({src: 'sfx/whoosh_trans.wav', at: h.t - 0.15, vol: 0.18, dur: 0.6})),
  ...DESTELLOS.slice(0, 5).map((t) => ({src: 'sfx/flash.wav', at: t - 0.02, vol: 0.22, dur: 0.6})),
  // garabatos
  {...ROT(0), at: ws(3)},
  {...ROT(1), at: ws(11) + 0.2},
  {...ROT(2), at: ws(20)},
  {src: 'sfx/subrayado.wav', at: ws(29) + 0.25, vol: 0.5, dur: 1.0},
  {...ROT(0), at: ws(38)},
  {...ROT(1), at: ws(67)},
  {...ROT(2), at: ws(74) + 0.1},
  {...ROT(0), at: ws(112)},
  {src: 'sfx/subrayado.wav', at: ws(130), vol: 0.5, dur: 1.0},
  {...ROT(1), at: ws(137) + 0.2},
  {...ROT(2), at: ws(152) + 0.2},
  {...ROT(0), at: ws(157) + 0.4},
  {...ROT(1), at: ws(165) + 0.4},
  // piezas que caen
  {src: 'sfx/pop.wav', at: ws(8), vol: 0.24},
  {src: 'sfx/pop.wav', at: ws(10), vol: 0.22},
  {src: 'sfx/whoosh_d.wav', at: ws(50) - 0.08, vol: 0.22, dur: 0.7},
  {src: 'sfx/pop.wav', at: ws(57), vol: 0.24},
  {src: 'sfx/whoosh_a.wav', at: ws(74) - 0.08, vol: 0.24, dur: 0.6},
  {src: 'sfx/notif.wav', at: ws(83), vol: 0.42},
  {src: 'sfx/pop.wav', at: ws(99), vol: 0.24},
  {src: 'sfx/pop.wav', at: ws(102), vol: 0.24},
  {src: 'sfx/pop.wav', at: ws(109), vol: 0.24},
  {src: 'sfx/whoosh_d.wav', at: ws(125) - 0.08, vol: 0.22, dur: 0.7},
  {src: 'sfx/pop.wav', at: ws(136), vol: 0.26},
  {src: 'sfx/pop.wav', at: ws(144), vol: 0.24},
  {src: 'sfx/pop.wav', at: ws(150), vol: 0.24},
  {src: 'sfx/whoosh_a.wav', at: ws(151) - 0.08, vol: 0.22, dur: 0.6},
  {src: 'sfx/obturador.wav', at: ws(156) - 0.03, vol: 0.5, dur: 1.0},
  // sellos
  {src: 'sfx/hit.wav', at: ws(48), vol: 0.32, dur: 1.2},
  {src: 'sfx/hit.wav', at: ws(89), vol: 0.32, dur: 1.2},
  {src: 'sfx/boom.wav', at: ws(112), vol: 0.26, dur: 1.4},
  {src: 'sfx/boom.wav', at: ws(165), vol: 0.32, dur: 1.6},
  // cierre
  {src: 'sfx/pop.wav', at: T.end + 0.4, vol: 0.26},
  {...ROT(2), at: T.end + 0.9},
];
SPEC_D.sfx = sfx;
// whoosh en cada línea de texto que entra, sin pisar otros efectos (< 0,35 s)
const titleSfx: Sfx[] = [];
TITLES.forEach((t, ti) =>
  t.lines.forEach((l, li) => {
    const at = l.words[0].at - 0.06;
    if ([...SPEC_D.sfx, ...titleSfx].some((x) => Math.abs(x.at - at) < 0.35)) return;
    titleSfx.push({src: ['sfx/whoosh_a.wav', 'sfx/whoosh_b.wav', 'sfx/whoosh_c.wav'][(ti + li) % 3], at, vol: l.color === 'purple' ? 0.24 : 0.18, dur: 0.7});
  }),
);
SPEC_D.sfx = [...SPEC_D.sfx, ...titleSfx];
void we;
