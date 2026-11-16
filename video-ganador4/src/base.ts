import {loadFont} from '@remotion/fonts';
import {Easing, staticFile} from 'remotion';
import {SPEECH, WORDS} from './timeline';

// Ganador 4 · «Los 3 problemas de las redes» — 1080x1920 a 60 fps (estilo.md).
export const FPS = 60;
export const W = 1080;
export const H = 1920;
export const OUTRO = 1.8; // cierre con logo
export const TOTAL = SPEECH + OUTRO;

// Colores del logo GROW (estilo.md §9.1) + lienzo del referente (§4.2)
export const P = {
  purple: '#B701FC',
  mid: '#9601FD',
  deep: '#7600FC',
  white: '#FFFFFF',
  lav: '#D8D8E6',
  grid: '#C9C9DB',
  ink: '#6E6E80',
};

// Tipografía (estilo.md §2): grotesca fina + la misma en negrita; serif cursiva solo para el adorno del gancho.
export const SANS = 'InterDisplayG4';
export const SERIF = 'PlayfairG4';
const pesos: [string, string][] = [
  ['Light', '300'],
  ['Regular', '400'],
  ['SemiBold', '600'],
  ['Bold', '700'],
  ['ExtraBold', '800'],
];
for (const [n, w] of pesos) loadFont({family: SANS, url: staticFile(`fonts/InterDisplay-${n}.otf`), weight: w, format: 'opentype'});
loadFont({family: SERIF, url: staticFile('fonts/PlayfairDisplay-Italic.woff2'), weight: '400', style: 'italic', format: 'woff2'});

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const backOut = Easing.bezier(0.34, 1.56, 0.64, 1);

/** Inicio / fin de la palabra i en la línea de tiempo (s). */
export const ws = (i: number) => WORDS[i].s;
export const we = (i: number) => WORDS[i].e;
/** Segundos → fotogramas. */
export const fr = (t: number) => Math.round(t * FPS);
