// Ganador 1 · "Hay 2 tipos de redes" (tomas 4856, 4847, 4852, 4866).
// Tiempos en segundos de la línea de tiempo, anclados a palabras (ws(i) = inicio de la palabra i).
import {wordTimes} from '../engine/helpers';
import {Spec, TitleDef, TitleWord} from '../engine/types';
import {FACES} from './faces';
import {SEGMENTS, SPEECH_FRAMES, WORDS} from './timeline';

const {ws, we} = wordTimes(WORDS);
const tw = (i: number, text?: string): TitleWord => ({text: text ?? WORDS[i].text.replace(/[,.¿?]/g, '').toLowerCase(), at: ws(i)});
const segStart = (i: number) => SEGMENTS[i].start / 30;
const segEnd = (i: number) => (SEGMENTS[i].start + SEGMENTS[i].srcOut - SEGMENTS[i].srcIn) / 30;

const TAIL = 2.3;
export const TOTAL = SPEECH_FRAMES / 30 + TAIL;

// ---------- escenas propias ----------
export const SC = {
  versus: {start: segStart(2) - 0.05, end: segEnd(3), top: ws(12), bottom: ws(16)},
  vacio: {start: ws(29) - 0.08, end: ws(38)},
  checklist: {start: ws(76) - 0.05, end: ws(82), items: [
    {t: 'Estrategia', at: ws(81)},
    {t: 'Contenido', at: ws(85)},
    {t: 'Fotos profesionales', at: ws(89)},
    {t: 'Publicidad paga', at: ws(100)},
  ]},
  encuesta: {start: ws(107) - 0.1, end: SPEECH_FRAMES / 30 + 0.05, no: ws(114), si: ws(119)},
};

const titles: TitleDef[] = [
  {
    id: 'gancho', start: ws(5), end: ws(10) - 0.12, y: 'head', overlap: 80, scene: true,
    lines: [
      {words: [tw(5, '2'), tw(6), tw(7)], color: 'white', size: 92, dx: -40},
      {words: [tw(8), tw(9)], color: 'purple', size: 120, dx: 30},
    ],
    covers: [5, 6, 7, 8, 9],
  },
  {
    id: 'diferencia', start: ws(20), end: ws(24) - 0.03, y: 'head', overlap: 80, scene: true,
    lines: [
      {words: [tw(19, '¿sabes'), tw(20), tw(21)], color: 'white', size: 84, dx: -30},
      {words: [tw(22), tw(23, 'diferencia?')], color: 'purple', size: 116, dx: 40},
    ],
    covers: [19, 20, 21, 22, 23],
  },
  {
    id: 'publicacion', start: ws(31), end: ws(38) - 0.05, y: 330,
    lines: [
      {words: [tw(31), tw(32), tw(33)], color: 'white', size: 84},
      {words: [tw(34), tw(35)], color: 'purple', size: 100},
    ],
    covers: [31, 32, 33, 34, 35],
  },
  {
    id: 'redsocial', start: ws(41), end: ws(47) - 0.03, y: 'head', overlap: 80, scene: true,
    lines: [
      {words: [tw(41), tw(42), tw(43), tw(44)], color: 'white', size: 84, dx: -30},
      {words: [tw(45), tw(46)], color: 'purple', size: 132, dx: 30},
    ],
    covers: [41, 42, 43, 44, 45, 46],
  },
  {
    id: 'vecinos', start: ws(56), end: ws(60) - 0.03, y: 340,
    lines: [
      {words: [tw(56), tw(57)], color: 'white', size: 100},
      {words: [tw(58), tw(59)], color: 'purple', size: 124},
    ],
    covers: [56, 57, 58, 59],
  },
  {
    id: 'sivenden', start: ws(61), end: ws(65) - 0.03, y: 'head', overlap: 90, scene: true,
    lines: [
      {words: [tw(61), tw(62), tw(63)], color: 'white', size: 92, dx: -30},
      {words: [tw(64)], color: 'purple', size: 150, dx: 30},
    ],
    covers: [61, 62, 63, 64],
  },
  {
    id: 'equipo', start: ws(72), end: ws(76) - 0.08, y: 400,
    lines: [
      {words: [tw(72), tw(73), tw(74)], color: 'white', size: 96},
      {words: [tw(75)], color: 'purple', size: 140},
    ],
    covers: [72, 73, 74, 75],
  },
  {
    id: 'contenido', start: ws(83), end: ws(86) - 0.03, y: 380,
    lines: [
      {words: [tw(83), tw(84)], color: 'white', size: 100},
      {words: [tw(85)], color: 'purple', size: 140},
    ],
    covers: [83, 84, 85],
  },
  {
    id: 'fotos', start: ws(88), end: ws(91) - 0.08, y: 380,
    lines: [
      {words: [tw(88), tw(89)], color: 'white', size: 104},
      {words: [tw(90)], color: 'purple', size: 124},
    ],
    covers: [88, 89, 90],
  },
  {
    id: 'clientes', start: ws(94), end: ws(99) - 0.05, y: 'head', overlap: 80, scene: true,
    lines: [
      {words: [tw(94), tw(95), tw(96)], color: 'white', size: 84, dx: -30},
      {words: [tw(97), tw(98)], color: 'purple', size: 128, dx: 30},
    ],
    covers: [94, 95, 96, 97, 98],
  },
  {
    id: 'publicidad', start: ws(99), end: ws(102) - 0.08, y: 330,
    lines: [
      {words: [tw(99), tw(100)], color: 'white', size: 104},
      {words: [tw(101)], color: 'purple', size: 150},
    ],
    covers: [99, 100, 101],
  },
  {
    id: 'pregunta', start: ws(103), end: ws(107) - 0.15, y: 'head', overlap: 90, scene: true,
    lines: [
      {words: [tw(103), tw(104), tw(105)], color: 'white', size: 92, dx: -30},
      {words: [tw(106)], color: 'purple', size: 140, dx: 30},
    ],
    covers: [103, 104, 105, 106],
  },
];

export const SPEC: Spec = {
  id: 'v9',
  clipPrefix: 'v9',
  segments: SEGMENTS,
  words: WORDS,
  faces: FACES,
  framing: {
    0: {scale: [1, 1], zoom: {from: 1.0, to: 1.22, s: 0.1, e: 1.2}},
    1: {scale: [1.22, 1.26], zoom: {from: 1.0, to: 1.0, s: 0, e: 1}},
    2: {scale: [1.0, 1.03]},
    3: {scale: [1.0, 1.03]},
    4: {scale: [1.24, 1.28]},
    5: {scale: [1.0, 1.04]},
    6: {scale: [1.0, 1.03]},
    7: {scale: [1.0, 1.06]},
    8: {scale: [1.26, 1.3]},
    9: {scale: [1.04, 1.08]},
    10: {scale: [1.0, 1.04]},
    11: {scale: [1.0, 1.03]},
    12: {scale: [1.18, 1.24]},
    13: {scale: [1.24, 1.28]},
    14: {scale: [1.0, 1.04]},
    15: {scale: [1.2, 1.24]},
    16: {scale: [1.0, 1.04]},
  },
  titles,
  noSubs: [
    [SC.versus.start, SC.versus.end],
    [SC.checklist.start, SC.checklist.end],
    [SC.encuesta.start, 999],
  ],
  broll: [
    {src: 'broll/v9_fotografo.mp4', start: ws(70) - 0.05, end: ws(76) - 0.05, trim: 1, zoom: [1.06, 1.0]},
    {src: 'broll/bts_camara.mp4', start: ws(82), end: ws(86), trim: 1.5, zoom: [1.0, 1.08]},
    {src: 'broll/v9_lente.mp4', start: ws(86), end: ws(91), trim: 0.5, zoom: [1.1, 1.0]},
  ],
  cards: [
    {src: 'broll/v9_tienda.mp4', start: ws(47), end: ws(56), trim: 0.2, y: 1000, width: 900, aspect: 16 / 9, rotate: -2},
    {src: 'broll/v9_amigos.mp4', start: ws(56), end: ws(60), trim: 3, y: 1000, width: 900, aspect: 16 / 9, rotate: 2},
    {src: 'broll/v9_analitica.mp4', start: ws(99), end: ws(102), trim: 1, y: 1000, width: 920, aspect: 16 / 9, rotate: -2},
  ],
  defocus: [
    [SC.vacio.start, SC.vacio.end],
    [ws(47), ws(60)],
    [ws(99), ws(102)],
  ],
  flashes: [SC.versus.start, SC.checklist.start, ws(89), SC.encuesta.start],
  whips: [SC.vacio.start, ws(47), ws(70) - 0.05, ws(86)],
  pulses: [ws(18), ws(60), ws(102)],
  music: {src: 'music/v9_lilpump.wav', volume: 0.085, fadeOutAt: TOTAL - 0.9},
  sfx: [],
  total: TOTAL,
  end: {start: SPEECH_FRAMES / 30 + 0.05, words: [
    {t: '¿del que vende', at: SPEECH_FRAMES / 30 + 0.35},
    {t: 'o del que no?', at: SPEECH_FRAMES / 30 + 0.65},
    {t: 'coméntalo', at: SPEECH_FRAMES / 30 + 1.0},
  ]},
};

// ---------- efectos de sonido (estilo.md §8) ----------
const titleSfx = titles.flatMap((t, ti) =>
  t.lines.slice(0, 2).map((l, li) => ({
    src: ['sfx/whoosh_a.wav', 'sfx/whoosh_b.wav', 'sfx/whoosh_c.wav'][(ti + li) % 3],
    at: l.words[0].at - 0.06,
    vol: l.color === 'purple' ? 0.3 : 0.22,
    dur: 0.7,
  })),
);
SPEC.sfx = [
  ...titleSfx,
  // versus
  {src: 'sfx/whoosh_long.wav', at: SC.versus.start - 0.1, vol: 0.26, dur: 1.2},
  {src: 'sfx/cash.wav', at: SC.versus.top, vol: 0.45},
  {src: 'sfx/hit.wav', at: SC.versus.bottom, vol: 0.28, dur: 1.2},
  // perfil vacío
  {src: 'sfx/whoosh_rocks.wav', at: SC.vacio.start - 0.1, vol: 0.22, dur: 1.4},
  {src: 'sfx/digital.wav', at: ws(34), vol: 0.22, dur: 0.6, trim: 0.5},
  // tienda / amigos
  {src: 'sfx/whoosh_d.wav', at: ws(47) - 0.08, vol: 0.25, dur: 0.9},
  {src: 'sfx/pop.wav', at: ws(56), vol: 0.24},
  {src: 'sfx/hit.wav', at: ws(60), vol: 0.24, dur: 1.0},
  // equipo + checklist
  {src: 'sfx/whoosh_trans.wav', at: ws(70) - 0.1, vol: 0.3},
  {src: 'sfx/flash.wav', at: SC.checklist.start, vol: 0.18, dur: 0.8},
  {src: 'sfx/click.wav', at: SC.checklist.items[0].at, vol: 0.6},
  {src: 'sfx/pop.wav', at: SC.checklist.items[0].at + 0.03, vol: 0.2},
  {src: 'sfx/whoosh_trans.wav', at: ws(86) - 0.05, vol: 0.3},
  {src: 'sfx/flash.wav', at: ws(89), vol: 0.35, dur: 1.0},
  {src: 'sfx/cash.wav', at: ws(98), vol: 0.4},
  // pregunta + encuesta
  {src: 'sfx/riser.wav', at: ws(103) - 2.6, vol: 0.26, dur: 2.6, trim: 1.0},
  {src: 'sfx/hit.wav', at: ws(103), vol: 0.3, dur: 1.2},
  {src: 'sfx/pop.wav', at: SC.encuesta.start + 0.05, vol: 0.3},
  {src: 'sfx/click.wav', at: SC.encuesta.no, vol: 0.5},
  {src: 'sfx/click.wav', at: SC.encuesta.si, vol: 0.6},
  {src: 'sfx/cash.wav', at: SC.encuesta.si + 0.15, vol: 0.35},
  // cierre
  {src: 'sfx/whoosh_long.wav', at: SPEECH_FRAMES / 30 - 0.1, vol: 0.26, dur: 1.2},
  {src: 'sfx/hit.wav', at: SPEECH_FRAMES / 30 + 0.05, vol: 0.28, dur: 1.4},
];
void we;
