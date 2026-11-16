// Ganador 3 · «Te tengo una buena noticia» + Grow Marketing — edición igual al REFERENTE GROW
// (estilo_referente_grow.md): un escenario distinto cada ~1 s al principio, palabras alrededor de la cabeza,
// títulos ultracondensados detrás de la persona, láminas moradas, palabras 3D, buscador curvado,
// demostración con la grabación de Instagram y cierre palabra a palabra.
import {wordTimes} from '../engine/helpers';
import {Sfx, Spec} from '../engine/types';
import {FACES} from '../v8/faces';
import {SEGMENTS, SPEECH_FRAMES, WORDS} from '../v8/timeline';

export const {ws, we} = wordTimes(WORDS);
export const SPEECH = SPEECH_FRAMES / 30;
export const TOTAL = SPEECH + 2.0;

// ---------- escenas ----------
export type Kind = 'estudio' | 'blanco' | 'escenario' | 'sala' | 'lamina' | 'palabras3d' | 'perfil' | 'google' | 'dm' | 'ig' | 'broll' | 'cierre';
export type Scene = {from: number; to: number; kind: Kind; dim?: boolean; word3d?: string; query?: string; src?: string};
export const SCENES: Scene[] = [
  {from: 0, to: 1.3, kind: 'estudio'},
  {from: 1.3, to: 1.8, kind: 'blanco'},
  {from: 1.8, to: 2.32, kind: 'lamina'},
  {from: 2.32, to: 3.33, kind: 'escenario'},
  {from: 3.33, to: 5.87, kind: 'sala'},
  {from: 5.87, to: 8.0, kind: 'palabras3d', word3d: 'REDES SOCIALES'},
  {from: 8.0, to: 11.07, kind: 'sala', dim: true},
  {from: 11.07, to: 12.43, kind: 'estudio'},
  {from: 12.43, to: 13.6, kind: 'escenario'},
  {from: 13.6, to: 17.1, kind: 'perfil'},
  {from: 17.1, to: 17.7, kind: 'lamina'},
  {from: 17.7, to: 20.7, kind: 'google', query: 'tienda de ropa cerca de mí'},
  {from: 20.7, to: 22.84, kind: 'sala', dim: true},
  {from: 22.84, to: 24.23, kind: 'dm'},
  {from: 24.23, to: 26.3, kind: 'sala'},
  {from: 26.3, to: 28.23, kind: 'palabras3d', word3d: 'OCUPADOS'},
  {from: 28.23, to: 29.0, kind: 'broll', src: 'broll/b8_tendero.mp4'},
  {from: 29.0, to: 29.85, kind: 'broll', src: 'broll/b8_barbero.mp4'},
  {from: 29.85, to: 30.67, kind: 'broll', src: 'broll/b8_empaque.mp4'},
  {from: 30.67, to: 32.2, kind: 'blanco'},
  {from: 32.2, to: 32.75, kind: 'lamina'},
  {from: 32.75, to: 34.5, kind: 'sala'},
  {from: 34.5, to: 35.55, kind: 'escenario'},
  {from: 35.55, to: 36.67, kind: 'sala', dim: true},
  {from: 36.67, to: 38.3, kind: 'google', query: 'grow marketing'},
  {from: 38.3, to: 44.36, kind: 'ig'},
  {from: 44.36, to: 45.94, kind: 'broll', src: 'broll/b8_foto.mp4'},
  {from: 45.94, to: 47.64, kind: 'sala'},
  {from: 47.64, to: 49.1, kind: 'lamina'},
  {from: 49.1, to: SPEECH, kind: 'sala', dim: true},
  {from: SPEECH, to: TOTAL, kind: 'cierre'},
];
export const sceneAt = (t: number) => SCENES.find((s) => t >= s.from && t < s.to) ?? SCENES[SCENES.length - 1];

/** Encuadre del recorte en cada escenario (escala anclada abajo al centro). */
// estudio/blanco a 1: los hombros (cortados por el borde de la toma) salen del cuadro, sin cortes rectos a la vista.
export const CUT_SCALE: Partial<Record<Kind, number>> = {estudio: 1, blanco: 1, escenario: 0.62, palabras3d: 0.7};

// ---------- textos ----------
/** Palabra suelta alrededor de la cabeza (gancho). behind = detrás de la persona. */
export type Hook = {i: number[]; text?: string; x: number; y: number; size: number; behind?: boolean; glow?: number};
export const HOOKS: Hook[] = [
  // «Te tengo una buena noticia.» (estudio morado)
  {i: [0], x: 250, y: 560, size: 110},
  {i: [1], x: 330, y: 700, size: 130, behind: true},
  {i: [2], x: 780, y: 690, size: 60, behind: true},
  {i: [3], x: 850, y: 820, size: 115, behind: true},
  {i: [4], x: 560, y: 1330, size: 128, glow: 2.4},
  // «Mira, hay una realidad que todo…» (estudio morado)
  {i: [40], x: 300, y: 560, size: 110},
  {i: [41, 42], x: 270, y: 730, size: 120},
  {i: [43], x: 790, y: 780, size: 130, behind: true},
  {i: [44, 45], x: 600, y: 1400, size: 118, glow: 2.4},
];

/** Título gigante ultracondensado detrás de la persona + palabra pequeña encima. */
export type Giant = {small: number[]; smallText?: string; big: number; bigText: string; color: 'gray' | 'purple'; y: number; size?: number; flip?: boolean};
export const GIANTS: Giant[] = [
  {small: [5], big: 6, bigText: 'TÚ', color: 'gray', y: 640, size: 620, flip: true},
  {small: [9, 10], big: 11, bigText: 'SOCIALES', color: 'purple', y: 700},
  {small: [46, 47], big: 48, bigText: 'DESCONOCE', color: 'purple', y: 700},
  {small: [110, 111], big: 112, bigText: 'TODÓLOGO', color: 'gray', y: 660, flip: true},
  {small: [124, 125, 126], big: 127, bigText: 'MARKETING', color: 'purple', y: 700},
];

/** Lámina morada a pantalla completa con palabras condensadas blancas que entran de golpe. */
export type Slide = {from: number; to: number; words: {i: number; text: string}[]; small?: string};
export const SLIDES: Slide[] = [
  {from: 1.8, to: 2.32, words: [{i: 7, text: 'NO'}, {i: 8, text: 'VENDES'}]},
  {from: 17.1, to: 17.7, words: [{i: 67, text: 'NO LE'}, {i: 69, text: 'GUSTA'}]},
  {from: 32.2, to: 32.75, words: [{i: 116, text: 'ESCUCHA'}]},
  {from: 47.64, to: 49.1, words: [{i: 164, text: 'SOMOS'}, {i: 165, text: '100%'}]},
];

/** Subtítulo de dos líneas a la izquierda (blanco + lavanda). */
export type TwoLine = {l1: number[]; l2: number[]};
export const TWOLINES: TwoLine[] = [
  {l1: [12, 13, 14], l2: [15, 16, 17]},
  {l1: [18, 19, 20], l2: [21]},
  {l1: [90, 91, 92, 93], l2: [94, 95, 96, 97]},
  {l1: [117, 118, 119], l2: [120, 121, 122, 123]},
  {l1: [158, 159, 160], l2: [161, 162, 163]},
];

/** Una palabra cada vez (centro-bajo): índices + tamaño 0 relleno / 1 normal / 2 destacada. */
export type One = {i: number[]; w: 0 | 1 | 2};
const one = (spec: string): One[] =>
  spec.split(' ').map((tok) => {
    const [ids, w] = tok.split(':');
    return {i: ids.split('+').map(Number), w: Number(w) as 0 | 1 | 2};
  });
export const ONES: One[] = [
  // «no es que las redes sociales no funcionen,» (palabras 3D)
  ...one('22:0 23+24:0 25:0 28:1 29:2'),
  // «es que tú la estás utilizando de una mala manera.» (sala oscurecida)
  ...one('30+31:0 32:1 33+34:1 35:2 36+37:0 38:2 39:2'),
  // «automáticamente pasa a un siguiente comercio» va en el buscador; «y si…» en el perfil
  // «o también pasa que a veces te escribe»
  ...one('76+77:1 78:1 79:0 80+81:1 82:0 83:2'),
  // «están ocupados en su día a día» (palabras 3D)
  ...one('98:1 99:2 100+101:0 102+103+104:1'),
  // «trabajando con su negocio, despachando» (B-roll)
  ...one('105:2 106+107:0 108:1 109:2'),
  // «que trabaje por ti.»
  ...one('128:0 129:1 130+131:2'),
  // «tomamos fotos profesionales» (B-roll)
  ...one('155:1 156:2 157:2'),
  // «profesionales en lo que hacemos.»
  ...one('167:2 168+169:0 170:0 171:2'),
];

// ---------- zooms de golpe (solo en la sala) ----------
export const SNAPS: {t: number; f: number}[] = [
  {t: ws(38), f: 1.08},
  {t: ws(83), f: 1.07},
  {t: ws(130), f: 1.08},
  {t: ws(171), f: 1.06},
];

// ---------- spec del motor ----------
export const SPEC_G: Spec = {
  id: 'v8g',
  clipPrefix: 'v8',
  segments: SEGMENTS,
  words: WORDS,
  faces: FACES,
  framing: {},
  titles: [],
  noSubs: [],
  broll: [],
  cards: [],
  defocus: [],
  flashes: [],
  whips: [],
  pulses: [],
  // corte en seco de la música en «Escucha» (como el corte de 13,7 s del referente)
  music: {src: 'music/v8g_nightdrive.wav', volume: 0.06, stopFrom: 32.08, stopTo: ws(117) - 0.02, fadeOutAt: TOTAL - 0.9},
  sfx: [],
  total: TOTAL,
};

// ---------- sonido (referente §9) ----------
const TECLAS = [2.63, 3.1, 3.42, 3.7, 4.1, 4.35, 4.7, 5.02, 5.35];
let k = 0;
const tecla = (at: number, vol = 0.3): Sfx => ({src: 'sfx/rg_teclado.wav', at, vol, dur: 0.26, trim: TECLAS[k++ % TECLAS.length]});
const textSfx: Sfx[] = [
  ...HOOKS.map((h) => tecla(ws(h.i[0]) - 0.02, 0.34)),
  ...GIANTS.flatMap((g) => [tecla(ws(g.small[0]) - 0.02, 0.3), tecla(ws(g.big) - 0.02, 0.4)]),
  ...SLIDES.flatMap((s) => s.words.map((w) => tecla(ws(w.i) - 0.02, 0.4))),
  ...TWOLINES.flatMap((l) => [...l.l1, ...l.l2].map((i) => tecla(ws(i) - 0.02, 0.22))),
  ...ONES.map((o) => tecla(ws(o.i[0]) - 0.02, o.w === 2 ? 0.3 : 0.2)),
];
SPEC_G.sfx = [
  {src: 'sfx/rg_click.wav', at: 0.06, vol: 0.6},
  {src: 'sfx/rg_lighter.wav', at: 0.08, vol: 0.35},
  // golpes graves en los títulos gigantes
  ...GIANTS.map((g) => ({src: 'sfx/rg_subbass.wav', at: ws(g.big), vol: 0.32, dur: 1.4})),
  // whooshes de los cortes grandes (mismos archivos que el referente)
  {src: 'sfx/rg_woosh4.wav', at: 5.87 - 0.2, vol: 0.3, dur: 1.2},
  {src: 'sfx/rg_whoosh3.wav', at: 13.6 - 0.12, vol: 0.3, dur: 1.1},
  {src: 'sfx/rg_whoosh2.wav', at: 17.7 - 0.12, vol: 0.28, dur: 1.1},
  {src: 'sfx/rg_whoosh3.wav', at: 22.84 - 0.12, vol: 0.28, dur: 1.1},
  {src: 'sfx/rg_woosh4.wav', at: 26.3 - 0.2, vol: 0.28, dur: 1.2},
  {src: 'sfx/rg_woosh8.wav', at: 32.08 - 0.3, vol: 0.34, dur: 0.4},
  {src: 'sfx/rg_deepbass.wav', at: ws(117) - 0.02, vol: 0.34, dur: 2.2},
  {src: 'sfx/rg_whoosh3.wav', at: 36.67 - 0.12, vol: 0.3, dur: 1.1},
  {src: 'sfx/rg_woosh10.wav', at: 38.3 - 0.05, vol: 0.32, dur: 1.5},
  {src: 'sfx/rg_whoosh2.wav', at: 41.0 - 0.1, vol: 0.22, dur: 1.0},
  {src: 'sfx/rg_woosh10.wav', at: 42.95 - 0.05, vol: 0.3, dur: 1.5},
  {src: 'sfx/rg_woosh8.wav', at: 47.64 - 0.3, vol: 0.3, dur: 0.4},
  {src: 'sfx/rg_subbass.wav', at: ws(165), vol: 0.34, dur: 1.4},
  {src: 'sfx/rg_whoosh3.wav', at: SPEECH - 0.1, vol: 0.26, dur: 1.1},
  // interfaz: clics del cursor
  {src: 'sfx/rg_click.wav', at: ws(74) + 0.02, vol: 0.6},
  {src: 'sfx/rg_click.wav', at: 38.3 - 0.25, vol: 0.6},
  ...textSfx,
];
void we;
