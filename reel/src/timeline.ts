// Guion de edición del reel de Macizo. Los tiempos se anclan al VIDEO BASE original con at(segundos_originales),
// que los traduce al timeline final (src/data/edl.json). Las palabras se referencian por su índice en Whisper
// (src/data/words.json) con W0(i). Así, al cambiar cortes, todo sigue pegado a su frase.
import { EDL, at, word } from "./util";

export const VOICE_END = EDL.duration;
export const END_CARD = 2.6;
export const TOTAL = VOICE_END + END_CARD;

// ---------------------------------------------------------------------------------------------
// 1. Bloques de subtítulos cinéticos (estilo.md §2): palabras pequeñas + 1 destacada gigante.
// ---------------------------------------------------------------------------------------------
export type BlockStyle = "yellow" | "lime" | "white" | "title";
export type Block = {
  id: string;
  w: [number, number]; // rango de índices de palabra (inclusive)
  hl: number[]; // palabras destacadas
  style?: BlockStyle;
  y?: number; // centro vertical (0..1)
  x?: number; // centro horizontal (0..1)
  end?: number; // fin forzado
  skip?: number[]; // palabras que no se muestran
  hlText?: string; // texto alternativo para la destacada
  maxHl?: number; // tamaño máximo de la destacada (px)
  hlWidth?: number; // ancho objetivo de la destacada (px)
  strikeAt?: number; // tachado rojo a mano alzada sobre la destacada
};

export const BLOCKS: Block[] = [
  { id: "diseno-unico", w: [16, 22], hl: [21, 22], style: "title", y: 0.27, end: at(6.70) },
  { id: "silla-sentando", w: [24, 30], hl: [24], y: 0.62, end: at(11.47) },
  { id: "fabricamos", w: [31, 33], hl: [32], style: "title", y: 0.3, end: at(12.53) },
  { id: "danes", w: [34, 37], hl: [37], y: 0.62, end: at(13.73) },
  { id: "espectacular", w: [38, 38], hl: [38], style: "lime", y: 0.62, end: at(14.70) },
  { id: "eames", w: [39, 42], hl: [42], y: 0.64, end: at(15.75) },
  { id: "construida", w: [43, 48], hl: [46], y: 0.6, end: at(17.97) },
  { id: "piezas", w: [55, 59], hl: [59], y: 0.62, end: at(22.85) },
  { id: "construimos", w: [60, 64], hl: [63], style: "title", y: 0.3, end: at(23.88) },
  { id: "macizo", w: [65, 66], hl: [66], y: 0.6, end: at(24.97) },
  { id: "muchas-cosas", w: [67, 71], hl: [69, 70, 71], y: 0.62, end: at(26.30) },
  { id: "poliuretanos", w: [76, 81], hl: [78], style: "title", y: 0.32, end: at(33.25) },
  { id: "empresa", w: [93, 98], hl: [94], y: 0.3, end: at(39.50) },
  { id: "proyectos", w: [111, 118], hl: [115], y: 0.3, end: at(46.67) },
  { id: "lideres", w: [119, 123], hl: [120], style: "lime", y: 0.6, end: at(48.35) },
  { id: "gratuito", w: [124, 130], hl: [129, 130], y: 0.56, end: at(51.10), skip: [124] },
  { id: "hogar", w: [131, 134], hl: [133, 134], y: 0.32, end: at(52.83) },
  { id: "ideas", w: [135, 141], hl: [138], y: 0.3, end: at(55.83) },
  { id: "fantastico", w: [142, 143], hl: [143], style: "lime", y: 0.58, end: at(56.92) },
  { id: "clientes", w: [144, 147], hl: [147], y: 0.58, end: at(59.28) },
  { id: "monton", w: [167, 170], hl: [169], y: 0.3, end: at(68.10) },
  { id: "confian", w: [174, 179], hl: [177], y: 0.58, end: at(71.13) },
  { id: "maravilloso", w: [180, 186], hl: [186], y: 0.3, end: at(74.15) },
  { id: "por-fuera", w: [187, 192], hl: [191, 192], y: 0.58, end: at(76.37) },
  { id: "nada", w: [194, 199], hl: [199], y: 0.58, end: at(78.86) },
  { id: "ayudamos", w: [200, 203], hl: [202, 203], y: 0.3, end: at(80.15) },
  { id: "gusto", w: [206, 210], hl: [209], y: 0.6, end: at(82.65) },
  { id: "mejor", w: [211, 218], hl: [216, 217, 218], y: 0.3, end: at(84.53) },
  { id: "conjunto", w: [219, 225], hl: [224, 225], style: "lime", y: 0.58, end: VOICE_END },
];

// ---------------------------------------------------------------------------------------------
// 2. B-roll a pantalla completa (estilo.md §4): 1,0–2,4 s, literal a la frase, push-in 1,00→1,08.
// ---------------------------------------------------------------------------------------------
export type BRoll = {
  t0: number;
  t1: number;
  src: string; // ruta dentro de public/
  kind: "video" | "image";
  trim?: number; // segundos de inicio dentro del clip
  zoom?: [number, number];
  origin?: string; // transform-origin
  pos?: string; // object-position para imágenes
  blurIn?: boolean; // entra con desenfoque + zoom que se asienta
  rate?: number; // velocidad de reproducción (renders casi estáticos a 0,75x)
};

/** Instante en que él reaparece sentado en la silla (tras "esta es una silla de diseño único"). */
export const SEATED_AT = at(9.7);

export const BROLL: BRoll[] = [
  // Apertura: la silla sola (él está fuera de cuadro en el original de 5,9 s a 8,9 s) mientras dice
  // "esta es una silla de diseño único".
  { t0: 0, t1: SEATED_AT, src: "media/base.mp4", kind: "video", trim: 5.9, zoom: [1.0, 1.12], origin: "40% 78%", blurIn: true },
  { t0: at(11.47), t1: at(12.53), src: "media/broll1.mp4", kind: "video", trim: 0.2, zoom: [1.06, 1.14] },
  { t0: at(22.85), t1: at(23.88), src: "media/broll2.mp4", kind: "video", trim: 2.2, zoom: [1.0, 1.08] },
  { t0: at(30.52), t1: at(31.55), src: "media/broll2.mp4", kind: "video", trim: 5.33, zoom: [1.0, 1.06] },
  { t0: at(31.55), t1: at(32.25), src: "media/broll2.mp4", kind: "video", trim: 7.6, zoom: [1.04, 1.1] },
  { t0: at(32.25), t1: at(33.25), src: "media/foto7.jpg", kind: "image", zoom: [1.35, 1.5], origin: "30% 25%", pos: "50% 50%" },
  { t0: at(33.25), t1: at(39.50), src: "media/foto5.jpg", kind: "image", zoom: [1.12, 1.22], origin: "55% 40%", pos: "50% 30%" },
  { t0: at(43.93), t1: at(44.93), src: "media/broll2.mp4", kind: "video", trim: 8.65, zoom: [1.0, 1.06] },
  { t0: at(44.93), t1: at(46.67), src: "media/c301.mp4", kind: "video", trim: 1.0, zoom: [1.04, 1.12] },
  { t0: at(51.10), t1: at(52.83), src: "media/c271.mp4", kind: "video", trim: 1.0, zoom: [1.0, 1.08] },
  { t0: at(52.83), t1: at(54.15), src: "media/broll2.mp4", kind: "video", trim: 10.35, zoom: [1.0, 1.07] },
  { t0: at(54.15), t1: at(55.83), src: "media/broll2.mp4", kind: "video", trim: 11.6, zoom: [1.02, 1.08] },
  { t0: at(66.63), t1: at(69.45), src: "media/foto4.jpg", kind: "image", zoom: [1.05, 1.16], origin: "50% 40%", pos: "50% 50%" },
  // "para hacer de sus proyectos algo maravilloso": renders de proyectos terminados (corrección: nada de DJ).
  { t0: at(72.03), t1: at(72.03) + 0.55, src: "media/broll2.mp4", kind: "video", trim: 6.42, rate: 0.75, zoom: [1.0, 1.06] },
  { t0: at(72.03) + 0.55, t1: at(74.15), src: "media/broll2.mp4", kind: "video", trim: 13.58, rate: 0.75, zoom: [1.02, 1.1] },
  { t0: at(78.86), t1: at(79.55), src: "media/broll2.mp4", kind: "video", trim: 16.12, zoom: [1.0, 1.06] },
  { t0: at(79.55), t1: at(80.15), src: "media/foto6.jpg", kind: "image", zoom: [1.22, 1.3], origin: "50% 22%", pos: "50% 50%" },
  { t0: at(81.37), t1: at(83.18), src: "media/broll1.mp4", kind: "video", trim: 2.7, zoom: [1.02, 1.1] },
  { t0: at(83.18), t1: at(84.53), src: "media/broll2.mp4", kind: "video", trim: 0.0, zoom: [1.0, 1.08] },
];

// ---------------------------------------------------------------------------------------------
// 3. Cámara: punch-ins (estilo.md §6) y transiciones (§5).
// ---------------------------------------------------------------------------------------------
export const PUNCH_INS: { t0: number; t1: number; s: number }[] = [
  { t0: at(13.76), t1: at(14.72), s: 1.42 },
  { t0: at(17.24), t1: at(18.00), s: 1.36 },
  { t0: at(26.30), t1: at(30.52), s: 1.3 },
  { t0: at(47.10), t1: at(49.73), s: 1.48 },
  { t0: at(70.50), t1: at(72.03), s: 1.32 },
  { t0: at(75.94), t1: at(76.37), s: 1.38 },
  { t0: at(78.40), t1: at(78.86), s: 1.3 },
  { t0: at(80.15), t1: at(81.37), s: 1.22 },
  { t0: at(87.06), t1: VOICE_END, s: 1.36 },
];

/** Vuelta a cabeza parlante con desenfoque + zoom que se asienta en 8 fotogramas. */
export const BLUR_INS = [at(12.53), at(23.88), at(49.73), at(55.83), at(69.45), at(74.15), at(77.07), at(80.15), at(84.53)];
/** Flash de exposición de 3 fotogramas. */
export const FLASHES = [at(6.70), at(39.50), at(76.37), VOICE_END];
/** Parpadeo oscuro de 1 fotograma antes de cambiar de b-roll. */
export const FLICKERS = [at(32.22), at(44.90), at(54.12), at(83.15)];
/** Estelas de luz amarilla. */
export const STREAKS = [0.05, at(11.50), at(22.88), at(72.08)];

// ---------------------------------------------------------------------------------------------
// 4. Efectos de sonido (estilo.md §8 + correcciones del usuario: typing en los textos).
// ---------------------------------------------------------------------------------------------
export type Sfx = { t: number; src: string; vol: number; dur?: number };
const s = (t: number, name: string, vol: number, dur?: number): Sfx => ({ t, src: `sfx/${name}.wav`, vol, dur });
const typing = (t: number, dur: number, vol = 0.32) => s(t, "typing", vol, dur);
const W0 = (i: number) => word(i).start;

export const SFX: Sfx[] = [
  // Gancho
  s(0, "whoosh1", 0.45),
  s(0.02, "subhit", 0.4),
  typing(W0(21), 0.55),
  s(at(6.70), "flash", 0.4),
  s(at(6.70), "subhit", 0.45),
  s(W0(24), "pop", 0.28),
  // Fabricamos / diseño danés / Eames
  s(at(11.47), "whoosh3", 0.42),
  typing(W0(32), 0.45),
  s(at(12.53), "swoosh1", 0.4),
  s(W0(37), "pop", 0.3),
  s(W0(38), "subhit", 0.5),
  s(at(14.72), "shutter", 0.32),
  s(at(14.94), "shutter", 0.28),
  s(at(15.16), "shutter", 0.28),
  s(W0(42), "pop", 0.3),
  s(W0(46), "pop", 0.32),
  s(at(18.00), "pop", 0.34),
  typing(W0(50), 0.4),
  typing(W0(53), 0.5),
  // Piezas / construimos / Macizo / muchas cosas más
  s(W0(59), "pop", 0.3),
  s(at(22.85), "whoosh1", 0.42),
  typing(W0(63), 0.45),
  s(W0(66), "subhit", 0.5),
  s(at(24.99), "riser", 0.32),
  s(W0(69), "boom", 0.42),
  // Lista de servicios
  s(at(26.30), "swoosh2", 0.3),
  s(W0(73), "pop", 0.32),
  typing(W0(73) + 0.03, 0.35),
  s(W0(74), "pop", 0.32),
  typing(W0(74) + 0.03, 0.4),
  s(W0(75), "pop", 0.32),
  typing(W0(75) + 0.03, 0.45),
  s(at(30.52), "whoosh3", 0.42),
  typing(W0(78), 0.5),
  s(at(31.55), "swoosh2", 0.28),
  s(at(32.25), "swoosh1", 0.35),
  typing(W0(80), 0.45, 0.26),
  // Empresa / gráfico
  s(at(33.25), "whoosh1", 0.4),
  s(at(39.50), "hitwhoosh", 0.45),
  typing(at(39.55), 0.45),
  s(at(41.33), "riser_long", 0.3, 1.7),
  s(at(43.28), "whoosh2", 0.4),
  typing(W0(110), 0.45),
  s(at(43.93), "whoosh3", 0.4),
  s(at(44.93), "swoosh2", 0.28),
  s(W0(115), "pop", 0.3),
  // Líderes / gratuito / hogar / ideas
  s(W0(120), "boom", 0.55),
  s(W0(120), "swoosh1", 0.35),
  s(at(49.73), "whoosh1", 0.4),
  s(W0(129), "pop", 0.32),
  s(W0(130) + 0.15, "click", 0.45),
  typing(W0(130) + 0.18, 0.3),
  s(at(51.10), "whoosh3", 0.4),
  s(W0(133), "pop", 0.32),
  typing(W0(133) + 0.05, 0.4),
  s(at(52.83), "swoosh1", 0.35),
  s(W0(138), "pop", 0.3),
  s(at(54.15), "swoosh2", 0.3),
  s(at(55.83), "whoosh2", 0.35),
  s(W0(143), "subhit", 0.45),
  // Clientes
  s(W0(147), "pop", 0.3),
  // Logos de clientes flotando: pop + whoosh suave por logo, tecleo del rótulo "Nuestros clientes"
  typing(W0(155) - 0.12, 0.45, 0.24),
  s(W0(155), "pop", 0.34),
  s(W0(155), "swoosh1", 0.22),
  s(W0(157), "pop", 0.34),
  s(W0(157), "swoosh2", 0.22),
  s(W0(160), "pop", 0.34),
  s(W0(160), "swoosh1", 0.22),
  s(W0(164), "pop", 0.34),
  s(W0(164), "swoosh2", 0.22),
  s(at(66.63), "whoosh1", 0.4),
  s(W0(171), "pop", 0.3),
  typing(W0(171) + 0.03, 0.4),
  s(W0(173), "pop", 0.3),
  typing(W0(173) + 0.03, 0.4),
  s(at(69.45), "swoosh2", 0.35),
  s(W0(177), "subhit", 0.48),
  s(at(72.03), "whoosh3", 0.4),
  s(at(72.03) + 0.55, "swoosh2", 0.26),
  s(W0(186), "pop", 0.32),
  // CTA
  s(at(74.15), "swoosh1", 0.35),
  s(W0(191), "pop", 0.3),
  s(at(76.37), "hitwhoosh", 0.45),
  s(at(76.37), "boom", 0.6),
  typing(at(76.39), 0.35),
  s(at(77.07), "swoosh2", 0.35),
  s(W0(199), "pop", 0.32),
  s(at(78.86), "whoosh1", 0.4),
  s(at(79.55), "swoosh1", 0.28),
  s(W0(202), "subhit", 0.45),
  s(at(80.15), "swoosh1", 0.35),
  typing(at(80.57), 0.4),
  s(at(80.95), "click", 0.55),
  s(at(81.37), "whoosh2", 0.38),
  s(W0(209), "pop", 0.3),
  s(at(83.18), "swoosh1", 0.33),
  s(W0(216), "pop", 0.32),
  s(at(84.53), "whoosh3", 0.38),
  s(W0(224), "cinebass", 0.5),
  // Cierre
  s(VOICE_END, "whoosh2", 0.4),
  s(VOICE_END + 0.25, "swoosh1", 0.35),
  s(VOICE_END + 0.3, "subhit", 0.4),
  typing(VOICE_END + 0.7, 0.45),
  s(VOICE_END + 1.25, "click", 0.5),
];
