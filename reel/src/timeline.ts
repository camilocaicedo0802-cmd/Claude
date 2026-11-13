// Guion de edición del reel de Macizo. Todos los tiempos están en segundos del timeline final (ver src/data/edl.json).
// Las palabras se referencian por su índice en la transcripción de Whisper (src/data/words.json).
import { EDL, word } from "./util";

export const VOICE_END = EDL.duration; // 65,6 s
export const END_CARD = 2.2;
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
  { id: "sillas", w: [0, 5], hl: [5], y: 0.6 },
  { id: "premios", w: [6, 8], hl: [8], y: 0.58, end: 2.95 },
  { id: "no-sillas", w: [9, 15], hl: [14, 15], style: "white", y: 0.6, end: 4.12, strikeAt: 3.78 },
  { id: "diseno-unico", w: [16, 22], hl: [21, 22], style: "title", y: 0.27, end: 5.73 },
  { id: "silla-sentando", w: [24, 30], hl: [24], y: 0.62, end: 7.3 },
  { id: "fabricamos", w: [31, 33], hl: [32], style: "title", y: 0.3, end: 8.3 },
  { id: "danes", w: [34, 37], hl: [37], y: 0.62, end: 9.5 },
  { id: "espectacular", w: [38, 38], hl: [38], style: "lime", y: 0.62, end: 10.1 },
  { id: "eames", w: [39, 42], hl: [42], y: 0.64, end: 11.15 },
  { id: "construida", w: [43, 48], hl: [46], y: 0.6, end: 12.9 },
  { id: "piezas", w: [55, 59], hl: [59], y: 0.62, end: 16.95 },
  { id: "construimos", w: [60, 64], hl: [63], style: "title", y: 0.3, end: 17.85 },
  { id: "macizo", w: [65, 66], hl: [66], y: 0.3, end: 18.6 },
  { id: "muchas-cosas", w: [67, 71], hl: [69, 70, 71], y: 0.62, end: 19.93 },
  { id: "poliuretanos", w: [76, 81], hl: [78], style: "title", y: 0.32, end: 25.95 },
  { id: "empresa", w: [93, 98], hl: [94], y: 0.3, end: 27.0 },
  { id: "proyectos", w: [111, 118], hl: [115], y: 0.3, end: 33.2 },
  { id: "lideres", w: [119, 123], hl: [120], style: "lime", y: 0.6, end: 34.88 },
  { id: "gratuito", w: [124, 130], hl: [129, 130], y: 0.56, end: 36.27, skip: [124] },
  { id: "hogar", w: [131, 134], hl: [133, 134], y: 0.32, end: 38.0 },
  { id: "ideas", w: [135, 141], hl: [138], y: 0.3, end: 40.5 },
  { id: "fantastico", w: [142, 143], hl: [143], style: "lime", y: 0.58, end: 41.35 },
  { id: "clientes", w: [144, 147], hl: [147], y: 0.58, end: 43.05 },
  { id: "monton", w: [167, 170], hl: [169], y: 0.3, end: 48.4 },
  { id: "confian", w: [174, 179], hl: [177], y: 0.58, end: 51.3 },
  { id: "maravilloso", w: [180, 186], hl: [186], y: 0.3, end: 53.95 },
  { id: "por-fuera", w: [187, 192], hl: [191, 192], y: 0.58, end: 55.8 },
  { id: "nada", w: [194, 199], hl: [199], y: 0.58, end: 58.06 },
  { id: "ayudamos", w: [200, 203], hl: [202, 203], y: 0.3, end: 59.35 },
  { id: "gusto", w: [206, 210], hl: [209], y: 0.6, end: 61.22 },
  { id: "mejor", w: [211, 218], hl: [216, 217, 218], y: 0.3, end: 63.1 },
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
};

export const BROLL: BRoll[] = [
  { t0: 7.3, t1: 8.3, src: "media/broll1.mp4", kind: "video", trim: 0.2, zoom: [1.06, 1.14] },
  { t0: 16.95, t1: 17.85, src: "media/broll2.mp4", kind: "video", trim: 2.2, zoom: [1.0, 1.08] },
  { t0: 17.85, t1: 18.6, src: "media/broll2.mp4", kind: "video", trim: 3.75, zoom: [1.02, 1.1] },
  { t0: 23.55, t1: 24.25, src: "media/broll2.mp4", kind: "video", trim: 5.33, zoom: [1.0, 1.06] },
  { t0: 24.25, t1: 24.95, src: "media/broll2.mp4", kind: "video", trim: 7.6, zoom: [1.04, 1.1] },
  { t0: 24.95, t1: 25.95, src: "media/foto7.jpg", kind: "image", zoom: [1.35, 1.5], origin: "30% 25%", pos: "50% 50%" },
  { t0: 25.95, t1: 27.0, src: "media/foto5.jpg", kind: "image", zoom: [1.12, 1.22], origin: "55% 40%", pos: "50% 30%" },
  { t0: 30.9, t1: 31.9, src: "media/broll2.mp4", kind: "video", trim: 8.65, zoom: [1.0, 1.06] },
  { t0: 31.9, t1: 33.2, src: "media/c301.mp4", kind: "video", trim: 1.0, zoom: [1.04, 1.12] },
  { t0: 36.27, t1: 38.0, src: "media/c271.mp4", kind: "video", trim: 1.0, zoom: [1.0, 1.08] },
  { t0: 38.0, t1: 39.05, src: "media/broll2.mp4", kind: "video", trim: 10.35, zoom: [1.0, 1.07] },
  { t0: 39.05, t1: 40.5, src: "media/broll2.mp4", kind: "video", trim: 11.6, zoom: [1.02, 1.08] },
  { t0: 47.4, t1: 49.75, src: "media/foto4.jpg", kind: "image", zoom: [1.05, 1.16], origin: "50% 40%", pos: "50% 50%" },
  { t0: 52.2, t1: 53.95, src: "media/c187.mp4", kind: "video", trim: 2.0, zoom: [1.0, 1.08] },
  { t0: 58.06, t1: 58.75, src: "media/broll2.mp4", kind: "video", trim: 16.12, zoom: [1.0, 1.06] },
  { t0: 58.75, t1: 59.35, src: "media/foto6.jpg", kind: "image", zoom: [1.22, 1.3], origin: "50% 22%", pos: "50% 50%" },
  { t0: 60.2, t1: 61.75, src: "media/broll1.mp4", kind: "video", trim: 2.7, zoom: [1.02, 1.1] },
  { t0: 61.75, t1: 63.1, src: "media/broll2.mp4", kind: "video", trim: 0.0, zoom: [1.0, 1.08] },
];

// ---------------------------------------------------------------------------------------------
// 3. Cámara: punch-ins (estilo.md §6) y transiciones (§5).
// ---------------------------------------------------------------------------------------------
export const PUNCH_INS: { t0: number; t1: number; s: number }[] = [
  { t0: 1.58, t1: 2.97, s: 1.28 },
  { t0: 9.53, t1: 10.12, s: 1.42 },
  { t0: 12.17, t1: 12.93, s: 1.36 },
  { t0: 19.93, t1: 23.55, s: 1.3 },
  { t0: 33.63, t1: 34.9, s: 1.48 },
  { t0: 43.07, t1: 47.4, s: 1.22 },
  { t0: 50.67, t1: 52.2, s: 1.32 },
  { t0: 55.37, t1: 55.8, s: 1.38 },
  { t0: 57.6, t1: 58.06, s: 1.3 },
  { t0: 59.35, t1: 60.2, s: 1.22 },
  { t0: 65.06, t1: VOICE_END, s: 1.36 },
];

/** Vuelta a cabeza parlante con desenfoque + zoom que se asienta en 8 fotogramas. */
export const BLUR_INS = [8.3, 18.6, 34.9, 40.5, 49.75, 53.95, 56.4, 59.35, 63.1];
/** Flash de exposición de 3 fotogramas. */
export const FLASHES = [5.73, 27.0, 55.8, VOICE_END];
/** Parpadeo oscuro de 1 fotograma antes de cambiar de b-roll. */
export const FLICKERS = [17.82, 24.92, 31.87, 39.02, 61.72];
/** Estelas de luz amarilla. */
export const STREAKS = [4.56, 7.33, 16.98, 52.25];

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
  s(W0(5), "pop", 0.32),
  s(W0(8), "pop", 0.34),
  s(W0(8) + 0.08, "typing_digital", 0.18, 0.55),
  s(W0(9) - 0.04, "swoosh2", 0.35),
  s(3.78, "marker", 0.55),
  s(4.53, "whoosh2", 0.42),
  typing(W0(21), 0.55),
  s(5.73, "flash", 0.4),
  s(5.73, "subhit", 0.45),
  s(W0(24), "pop", 0.28),
  // Fabricamos / diseño danés / Eames
  s(7.3, "whoosh3", 0.42),
  typing(W0(32), 0.45),
  s(8.3, "swoosh1", 0.4),
  s(W0(37), "pop", 0.3),
  s(W0(38), "subhit", 0.5),
  s(10.12, "shutter", 0.32),
  s(10.34, "shutter", 0.28),
  s(10.56, "shutter", 0.28),
  s(W0(42), "pop", 0.3),
  s(W0(46), "pop", 0.32),
  s(12.93, "pop", 0.34),
  typing(W0(50), 0.4),
  typing(W0(53), 0.5),
  // Piezas / construimos / Macizo / muchas cosas más
  s(W0(59), "pop", 0.3),
  s(16.95, "whoosh1", 0.42),
  typing(W0(63), 0.45),
  s(17.85, "swoosh1", 0.35),
  s(W0(66), "subhit", 0.5),
  s(18.6, "whoosh2", 0.38),
  s(18.62, "riser", 0.32),
  s(W0(69), "boom", 0.42),
  // Lista de servicios
  s(19.93, "swoosh2", 0.3),
  s(W0(73), "pop", 0.32),
  typing(W0(73) + 0.03, 0.35),
  s(W0(74), "pop", 0.32),
  typing(W0(74) + 0.03, 0.4),
  s(W0(75), "pop", 0.32),
  typing(W0(75) + 0.03, 0.45),
  s(23.55, "whoosh3", 0.42),
  typing(W0(78), 0.5),
  s(24.25, "swoosh2", 0.28),
  s(24.95, "swoosh1", 0.35),
  typing(W0(80), 0.45, 0.26),
  // Empresa / gráfico
  s(25.95, "whoosh1", 0.4),
  s(27.0, "hitwhoosh", 0.45),
  typing(27.05, 0.45),
  s(28.3, "riser_long", 0.3, 1.7),
  s(30.25, "whoosh2", 0.4),
  typing(W0(110), 0.45),
  s(30.9, "whoosh3", 0.4),
  s(31.9, "swoosh2", 0.28),
  s(W0(115), "pop", 0.3),
  // Líderes / gratuito / hogar / ideas
  s(W0(120), "boom", 0.55),
  s(W0(120), "swoosh1", 0.35),
  s(34.9, "whoosh1", 0.4),
  s(W0(129), "pop", 0.32),
  s(W0(130) + 0.15, "click", 0.45),
  typing(W0(130) + 0.18, 0.3),
  s(36.27, "whoosh3", 0.4),
  s(W0(133), "pop", 0.32),
  typing(W0(133) + 0.05, 0.4),
  s(38.0, "swoosh1", 0.35),
  s(W0(138), "pop", 0.3),
  s(39.05, "swoosh2", 0.3),
  s(40.5, "whoosh2", 0.35),
  s(W0(143), "subhit", 0.45),
  // Clientes
  s(W0(147), "pop", 0.3),
  s(43.07, "pop", 0.34),
  typing(W0(155), 0.4),
  s(W0(156) + 0.25, "pop", 0.26),
  typing(W0(157), 0.4),
  s(W0(158) + 0.3, "pop", 0.26),
  typing(W0(160), 0.6),
  s(W0(163) + 0.3, "pop", 0.26),
  typing(W0(164), 0.5),
  s(W0(166) + 0.3, "pop", 0.26),
  s(47.4, "whoosh1", 0.4),
  s(W0(171), "pop", 0.3),
  typing(W0(171) + 0.03, 0.4),
  s(W0(173), "pop", 0.3),
  typing(W0(173) + 0.03, 0.4),
  s(49.75, "swoosh2", 0.35),
  s(W0(177), "subhit", 0.48),
  s(52.2, "whoosh3", 0.4),
  s(W0(186), "pop", 0.32),
  // CTA
  s(53.95, "swoosh1", 0.35),
  s(W0(191), "pop", 0.3),
  s(55.8, "hitwhoosh", 0.45),
  s(55.8, "boom", 0.6),
  typing(55.82, 0.35),
  s(56.4, "swoosh2", 0.35),
  s(W0(199), "pop", 0.32),
  s(58.06, "whoosh1", 0.4),
  s(58.75, "swoosh1", 0.28),
  s(W0(202), "subhit", 0.45),
  s(59.35, "swoosh1", 0.35),
  typing(59.4, 0.4),
  s(59.78, "click", 0.55),
  s(60.2, "whoosh2", 0.38),
  s(W0(209), "pop", 0.3),
  s(61.75, "swoosh1", 0.33),
  s(W0(216), "pop", 0.32),
  s(63.1, "whoosh3", 0.38),
  s(W0(224), "cinebass", 0.5),
  // Cierre
  s(VOICE_END, "whoosh2", 0.4),
  typing(VOICE_END + 0.25, 0.6),
  s(VOICE_END + 0.95, "click", 0.5),
];
