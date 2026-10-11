import { palabras } from "../data/palabras";
import { FPS } from "./theme";

export const seg = (s: number) => Math.round(s * FPS);

// Fotograma global en el que se pronuncia la palabra i de la locución.
export const pf = (i: number) => Math.round((palabras[i].startMs / 1000) * FPS);
export const pfEnd = (i: number) =>
  Math.round((palabras[i].endMs / 1000) * FPS);

// Las palabras empiezan a entrar 5 fotogramas antes de pronunciarse (estilo.md §3.5).
export const ADELANTO = 5;

// Índices de palabras (ver src/data/palabras.ts).
export const P = {
  todo: 0,
  comenzo: 1,
  en: 2,
  una: 3,
  pequena: 4,
  isla: 5,
  de: 6,
  portugal: 7,
  donde: 8,
  un: 9,
  nino: 10,
  tenia: 11,
  un2: 12,
  sueno: 13,
  mas: 14,
  grande: 15,
  que: 16,
  sus: 17,
  posibilidades: 18,
  De: 19,
  madeira: 20,
  al: 21,
  manchester: 22,
  united: 23,
  del: 24,
  real: 25,
  madrid: 26,
  a: 27,
  conquistar: 28,
  el: 29,
  mundo: 30,
  disciplina: 31,
  sacrificio: 32,
  y: 33,
  una2: 34,
  ambicion: 35,
  imparable: 36,
  rompio: 37,
  records: 38,
  conquisto: 39,
  titulos: 40,
  y2: 41,
  escribio: 42,
  su: 43,
  propia: 44,
  historia: 45,
  Su: 46,
  nombre: 47,
  es: 48,
  cristiano: 49,
  ronaldo: 50,
  y3: 51,
  su2: 52,
  legado: 53,
  va: 54,
  mucho: 55,
  mas2: 56,
  alla: 57,
  del2: 58,
  futbol: 59,
} as const;
