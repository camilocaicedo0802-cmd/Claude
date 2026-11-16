import {OUTRO, TOTAL, we, ws} from './base';
import {CARAS} from './caras';
import {SEGMENTS, SPEECH} from './timeline';

// ------------------------------------------------------------------ planos (estilo.md §6)
// Zoom anclado abajo (la cabeza sube al tercio superior al acercar) y centrado en la cara del segmento.
// Niveles del referente: 1,00 · 1,12 · 1,23 · 1,40; el zoom cambia en cada corte.
export type Plano = {from: number; to: number; s0: number; s1: number; push?: {at: number; dur: number; to: number}};
export const PLANOS: Plano[] = [
  {from: 0, to: 3.27, s0: 1.12, s1: 1.16},
  {from: 3.27, to: 4.57, s0: 1.0, s1: 1.02},
  {from: 4.57, to: 10.23, s0: 1.0, s1: 1.03}, // dentro de la tarjeta del lienzo
  {from: 10.23, to: 13.27, s0: 1.4, s1: 1.43}, // primer plano
  {from: 13.27, to: 18.5, s0: 1.23, s1: 1.25}, // (bajo el B-roll y la maqueta)
  {from: 18.5, to: 20.97, s0: 1.12, s1: 1.15},
  {from: 20.97, to: 22.03, s0: 1.4, s1: 1.42},
  {from: 22.03, to: 24.87, s0: 1.0, s1: 1.03},
  {from: 24.87, to: 26.07, s0: 1.0, s1: 1.0, push: {at: 25.25, dur: 0.6, to: 1.2}}, // empuje animado (ref. 20,92 s)
  {from: 26.07, to: 30.2, s0: 1.2, s1: 1.16}, // deriva hacia atrás
  {from: 30.2, to: 33.4, s0: 1.12, s1: 1.12}, // (bajo la grabación de Grow)
  {from: 33.4, to: 34.93, s0: 1.23, s1: 1.26}, // 03 · ¿por qué elegirte?
  // cierre (toma 4868)
  {from: 34.93, to: 37.23, s0: 1.0, s1: 1.03},
  {from: 37.23, to: 39.33, s0: 1.23, s1: 1.25},
  {from: 39.33, to: 40.3, s0: 1.4, s1: 1.42},
  {from: 40.3, to: TOTAL, s0: 1.12, s1: 1.12, push: {at: 41.95, dur: 0.45, to: 1.12}}, // empuje en «ahora»
];

export const segAt = (t: number) => SEGMENTS.find((s, i) => t >= s.start && (i === SEGMENTS.length - 1 || t < SEGMENTS[i + 1].start)) ?? SEGMENTS[SEGMENTS.length - 1];
/** Centro x de la cara en el segmento (origen horizontal del zoom). */
export const caraX = (t: number) => CARAS[segAt(Math.min(t, SPEECH - 0.01)).idx][4];

// ------------------------------------------------------------------ texto (estilo.md §2)
export type Linea = {
  kind: 'small' | 'big' | 'single';
  words: number[];
  purple?: boolean;
  typed?: boolean; // letra a letra
  size?: number;
  dx?: number; // desplazamiento horizontal de la línea (escalonado)
  serif?: number[]; // palabras en serif cursiva (adorno)
  over?: Record<number, string>; // texto que se muestra en lugar de la palabra
};
export type Bloque = {lines: Linea[]; y: number; x?: number; box?: boolean; end?: number};

const sm = (words: number[], extra: Partial<Linea> = {}): Linea => ({kind: 'small', words, ...extra});
const bg = (words: number[], extra: Partial<Linea> = {}): Linea => ({kind: 'big', words, ...extra});
const rango = (a: number, b: number) => Array.from({length: b - a + 1}, (_, i) => a + i);

export const BLOQUES: Bloque[] = [
  // gancho
  {lines: [sm(rango(0, 4), {serif: [0]}), bg([5, 6], {purple: true})], y: 1335, x: 600},
  {lines: [sm([7, 8]), bg([9]), sm(rango(10, 12), {dx: 150})], y: 1335, x: 600},
  {lines: [sm([13]), bg([14, 15], {purple: true})], y: 1385, end: 4.5},
  // lienzo: los tres problemas
  {lines: [sm([16, 17])], y: 1300},
  {lines: [sm([18, 19]), bg([20], {purple: true})], y: 1320},
  {lines: [sm(rango(21, 25)), bg([26])], y: 1320, box: true},
  {lines: [sm([27, 28, 29])], y: 1320, end: 10.2},
  // primer plano
  {lines: [sm([30, 31]), bg([32], {typed: true})], y: 1130},
  {lines: [bg([33, 34], {purple: true})], y: 1120, end: 13.24},
  // B-roll: cliente mirando el móvil
  {lines: [sm([35]), bg([36])], y: 1560},
  {lines: [sm(rango(37, 40)), bg([41, 42])], y: 1560},
  {lines: [sm([43, 44, 45]), bg([46, 47, 48], {purple: true})], y: 1560, end: 17.0},
  // maqueta del perfil desordenado
  {lines: [sm(rango(49, 52)), bg([53], {purple: true})], y: 1660, end: 18.47},
  {lines: [sm([54, 55]), bg([56])], y: 1300},
  {lines: [sm(rango(57, 60)), bg([61, 62], {purple: true})], y: 1300, end: 20.94},
  // primer plano «Ya tienes que parar»
  {lines: [sm(rango(63, 65)), bg([66], {purple: true, size: 172})], y: 1065, end: 22.0},
  {lines: [{kind: 'single', words: [67]}], y: 1360},
  {lines: [{kind: 'single', words: [68]}], y: 1360},
  {lines: [{kind: 'single', words: [69]}], y: 1360},
  {lines: [bg([70, 71])], y: 1370},
  {lines: [sm([72, 73]), bg([74, 75], {purple: true})], y: 1560, end: 24.84},
  // solución
  {lines: [sm(rango(76, 78)), bg([79])], y: 1330},
  {lines: [sm(rango(80, 82)), bg([83])], y: 1270},
  {lines: [bg([84, 85], {purple: true, over: {84: '3'}, size: 150})], y: 1270},
  {lines: [sm(rango(86, 88)), sm(rango(89, 92), {dx: 90})], y: 1270, end: 30.17},
  // cierre (toma 4868): «Y lamentablemente, cuando no comunicas bien, tu cliente elige a otro comercio,
  // así que ya sabes, tienes que mejorar tus redes sociales ahora.»
  {lines: [sm([105]), bg([106])], y: 1410},
  {lines: [sm([107, 108]), bg([109, 110])], y: 1410, end: 37.2},
  {lines: [sm(rango(111, 114)), bg([115, 116], {purple: true})], y: 1270, end: 39.3},
  {lines: [sm([117, 118]), bg([119, 120])], y: 1120, end: 40.27},
  {lines: [sm([121, 122]), bg([123])], y: 1330},
  {lines: [sm([124]), bg([125, 126], {purple: true})], y: 1330},
  {lines: [bg([127], {purple: true, size: 200})], y: 1330, end: SPEECH - 0.02},
];

// Las tres cosas que debe responder el perfil (palabras 93-104), una por golpe con su número grande 01 · 02 · 03.
// («Número uno» se quitó del audio: nunca decía «dos» ni «tres» y parecía que solo enumeraba una.)
export const LISTA = [
  {n: '01', words: [93, 94, 95], clave: 95, pre: '¿', post: '?'},
  {n: '02', words: [96, 97, 98, 99, 100], clave: 98, pre: '¿', post: '?'},
  {n: '03', words: [102, 103, 104], clave: 104, pre: '¿', post: '?'},
];

// ------------------------------------------------------------------ escenas especiales
export const T = {
  gancho: {movil: ws(5) - 0.3, logos: [ws(5), ws(6), ws(8)], fin: 3.16},
  lienzo: {from: 4.57, to: 10.23, desorden: ws(20), numeros: [ws(16), ws(21), ws(28)], caja: ws(26)},
  rayas: 10.23,
  tecleo: {from: ws(32), to: we(32)},
  cliente: {from: 13.27, to: 17.04},
  maqueta: {from: 17.04, to: 18.5},
  parar: ws(66),
  escritorio: {from: 23.45, to: 24.87},
  marco: {from: ws(84) - 0.04, to: 34.93},
  grow: {from: 30.2, to: 33.4, mitad: 31.55},
  golpes: [ws(93) - 0.1, ws(96) - 0.1, ws(101) - 0.05],
  logos2: {logos: [ws(125), ws(126), ws(126) + 0.16], fin: SPEECH - 0.05},
  ahora: ws(127),
  cierre: {from: SPEECH, to: SPEECH + OUTRO},
};

/** Transiciones de desenfoque (estilo.md §5): centro y duración total. */
export const DESENFOQUES = [
  {at: 0, dur: 0.7, intro: true},
  {at: T.cliente.from, dur: 0.36},
  {at: T.cliente.to, dur: 0.3},
  {at: T.maqueta.to, dur: 0.3},
  {at: T.escritorio.from, dur: 0.3},
  {at: 24.87, dur: 0.4},
  {at: 34.93, dur: 0.36}, // del marco al cierre
  {at: SPEECH, dur: 0.3}, // al logo
];

// ------------------------------------------------------------------ sonido (estilo.md §8; solo SFX del pack del cliente)
export type Sfx = {src: string; at: number; vol: number; dur?: number; trim?: number};
const s = (src: string, at: number, vol: number, dur?: number, trim?: number): Sfx => ({src: `sfx/${src}.wav`, at, vol, dur, trim});

export const SFX: Sfx[] = [
  s('g4_whoosh_corto2', 0.02, 0.4, 1.2), // arranque desenfocado
  s('g4_woosh10', T.gancho.movil - 0.1, 0.42, 1.7), // entra el móvil 3D
  s('g4_impacto', T.gancho.movil + 0.38, 0.32, 2.0), // aterriza (ondas)
  ...T.gancho.logos.map((t) => s('g4_pop', t - 0.02, 0.3, 0.9)),
  s('g4_whoosh_corto2', T.gancho.fin - 0.08, 0.26, 1.0),
  s('g4_subbass', 3.27, 0.5, 1.5), // corte «tienen tres problemas»
  s('g4_woosh10', 3.2, 0.3, 1.7),
  s('g4_swoosh7', T.lienzo.from - 0.02, 0.55, 0.4), // se encoge a la tarjeta
  ...T.lienzo.numeros.map((t) => s('g4_click', t, 0.55, 0.3)),
  s('g4_swoosh5', T.lienzo.desorden - 0.05, 0.45, 0.4), // publicaciones desordenadas
  s('g4_swoosh3', T.lienzo.desorden + 0.12, 0.35, 0.4),
  s('g4_mechero', T.lienzo.caja - 0.03, 0.55, 0.4), // caja resaltada
  s('g4_click', T.rayas - 0.02, 0.6, 0.3), // rayas
  s('g4_bassdrop', T.rayas - 0.02, 0.32, 1.4),
  s('g4_woosh7', T.cliente.from - 0.2, 0.32, 1.6),
  s('g4_swoosh5', T.maqueta.from - 0.03, 0.45, 0.4),
  s('g4_swoosh7', T.maqueta.to - 0.03, 0.4, 0.4),
  s('g4_subbass', T.parar - 0.02, 0.55, 1.5), // «parar»
  s('g4_whoosh_corto2', 20.9, 0.3, 1.2),
  s('g4_woosh7', T.escritorio.from - 0.2, 0.3, 1.5),
  s('g4_woosh10', 24.8, 0.38, 1.7), // desenfoque «Mira, es muy sencillo»
  s('g4_swoosh3', 25.27, 0.3, 0.4), // empuje
  s('g4_mechero', T.marco.from, 0.6, 0.4), // marco «caja central»
  s('g4_obturador', T.grow.from - 0.02, 0.45, 0.4),
  ...T.golpes.map((t) => s('g4_click', t, 0.6, 0.3)), // 01 · 02 · 03
  ...T.golpes.map((t) => s('g4_swoosh3', t + 0.02, 0.32, 0.4)),
  s('g4_obturador', T.grow.mitad - 0.02, 0.4, 0.4),
  s('g4_woosh10', 34.86, 0.38, 1.7), // del marco al cierre
  s('g4_subbass', 34.93, 0.4, 1.5),
  s('g4_swoosh5', ws(115) - 0.05, 0.38, 0.4), // «otro comercio»
  s('g4_whoosh_corto2', 39.3, 0.28, 1.2), // primer plano «así que ya sabes»
  ...T.logos2.logos.map((t) => s('g4_pop', t - 0.02, 0.3, 0.9)), // logos de nuevo
  s('g4_subbass', T.ahora - 0.02, 0.55, 1.5), // «ahora»
  s('g4_impacto', T.cierre.from + 0.05, 0.34, 1.8), // cierre
];

// Música: ANBR – Quantum (carpeta del cliente), ~12 LU bajo la voz (§9.6); silencio en «Ya tienes que parar».
export const MUSICA = {src: 'music/g4_quantum.wav', vol: 0.075, corte: {from: 20.95, to: 22.0}, fadeOut: TOTAL - 1.0};
