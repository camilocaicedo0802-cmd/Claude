// PLAN DE EDICIÓN (todos los tiempos en segundos de la edición).
// Los índices de palabras apuntan a src/datos/edicion.json (ver lista en scripts).
import { DURACION_VOZ_S } from "./util";

// ---------- Bloques de subtítulos (cada bloque = palabras pequeñas + 1 destacado) ----------
export type EstiloBloque = "linea" | "detras" | "tecleada" | "broll";
export type Bloque = {
  estilo: EstiloBloque;
  desde: number; // s: el bloque se monta
  hasta: number; // s: el bloque sale
  pequenas: number[]; // índices de palabras pequeñas
  destacado: number[]; // índices de la palabra destacada (1-3 palabras)
  pildora?: number[]; // índices de palabras dentro de la píldora cian (b-roll)
  icono?: string; // emoji 3D (public/iconos/*.png) junto al destacado
  alerta?: boolean; // variante roja → blanca con "!"
  impacto?: boolean; // golpe grave al aparecer el destacado
};

export const BLOQUES: Bloque[] = [
  { estilo: "linea", desde: 0.0, hasta: 0.8, pequenas: [], destacado: [0], icono: "saludo" },
  { estilo: "detras", desde: 0.8, hasta: 3.0, pequenas: [1, 2, 3, 4, 5], destacado: [6], icono: "cocinero", impacto: true },
  { estilo: "broll", desde: 3.0, hasta: 4.17, pequenas: [7], destacado: [8] },
  { estilo: "tecleada", desde: 4.17, hasta: 5.57, pequenas: [9], destacado: [10], icono: "corriendo", impacto: true },
  { estilo: "linea", desde: 5.57, hasta: 7.45, pequenas: [11, 12, 13, 14, 15], destacado: [16] },
  { estilo: "linea", desde: 7.45, hasta: 8.57, pequenas: [17, 18], destacado: [19] },
  { estilo: "linea", desde: 8.57, hasta: 9.37, pequenas: [20], destacado: [21] },
  { estilo: "linea", desde: 9.37, hasta: 10.1, pequenas: [22, 23, 24, 25, 26], destacado: [] },
  { estilo: "broll", desde: 10.1, hasta: 12.2, pequenas: [], destacado: [27], pildora: [28, 29, 30, 31], icono: "manzana", impacto: true },
  { estilo: "detras", desde: 12.2, hasta: 13.05, pequenas: [32, 33, 34], destacado: [35] },
  { estilo: "linea", desde: 14.8, hasta: 17.0, pequenas: [42, 43, 44, 45], destacado: [46, 47, 48] },
  { estilo: "detras", desde: 17.0, hasta: 18.15, pequenas: [49, 50], destacado: [51], icono: "plato" },
  { estilo: "broll", desde: 18.15, hasta: 19.8, pequenas: [52, 53, 54], destacado: [55] },
  { estilo: "detras", desde: 19.8, hasta: 21.27, pequenas: [56], destacado: [57], impacto: true },
  { estilo: "broll", desde: 23.38, hasta: 24.95, pequenas: [65, 66, 67, 68, 69, 70, 71], destacado: [72], pildora: [73, 74], icono: "manzana" },
  { estilo: "tecleada", desde: 29.27, hasta: 30.5, pequenas: [88], destacado: [89, 90], impacto: true },
  { estilo: "linea", desde: 30.5, hasta: 32.43, pequenas: [91, 92, 93], destacado: [94, 95] },
  { estilo: "broll", desde: 32.43, hasta: 34.13, pequenas: [98, 99, 100], destacado: [101, 102], icono: "alarma" },
  { estilo: "linea", desde: 34.13, hasta: 34.89, pequenas: [103, 104, 105, 106], destacado: [107, 108], icono: "delicioso" },
  { estilo: "linea", desde: 34.89, hasta: DURACION_VOZ_S, pequenas: [109, 110, 111, 112, 113], destacado: [114, 115], icono: "amanecer" },
];

// ---------- Cámara del plano hablando (§2) ----------
// s = escala, y = desplazamiento vertical en px (positivo = el sujeto baja), d = duración (s)
export type Mov = { t: number; s: number; y: number; d: number; lineal?: boolean };
export const CAMARA: Mov[] = [
  { t: 0, s: 1.32, y: 0, d: 0 },
  { t: 0, s: 1.0, y: 0, d: 0.6 }, // zoom de salida de apertura
  { t: 0.8, s: 1.1, y: 0, d: 0.08 }, // punch
  { t: 1.9, s: 1.14, y: 60, d: 0.3 }, // reencuadre para ESPOSITO detrás
  { t: 4.17, s: 1.18, y: 0, d: 0 },
  { t: 4.17, s: 1.0, y: 0, d: 0.45 }, // vuelve de b-roll
  { t: 5.57, s: 1.1, y: 0, d: 0.08 },
  { t: 5.65, s: 1.17, y: -40, d: 2.9, lineal: true }, // empuje lento (deja sitio a la tarjeta)
  { t: 8.57, s: 1.02, y: 0, d: 0.08 },
  { t: 9.37, s: 1.14, y: 0, d: 0.08 },
  { t: 12.2, s: 1.22, y: 40, d: 0 },
  { t: 12.2, s: 1.08, y: 60, d: 0.5 }, // tras light leak + reencuadre para EXPLICABA
  { t: 14.8, s: 1.18, y: 0, d: 0 },
  { t: 14.8, s: 1.0, y: 0, d: 0.45 },
  { t: 16.2, s: 1.12, y: 0, d: 0.08 },
  { t: 16.95, s: 1.16, y: 60, d: 0.3 }, // para COME detrás
  { t: 19.8, s: 1.22, y: 60, d: 0 },
  { t: 19.8, s: 1.06, y: 60, d: 0.45 }, // GLUCOSA detrás + gráfica
  { t: 29.27, s: 1.18, y: 0, d: 0 },
  { t: 29.27, s: 1.0, y: 0, d: 0.45 },
  { t: 30.5, s: 1.1, y: 0, d: 0.08 },
  { t: 30.6, s: 1.17, y: -40, d: 1.8, lineal: true },
  { t: 34.13, s: 1.18, y: 0, d: 0 },
  { t: 34.13, s: 1.0, y: 0, d: 0.45 },
  { t: 34.89, s: 1.12, y: 0, d: 0.08 },
];

// ---------- Escenas a pantalla completa (tapan el plano hablando) ----------
export type Escena =
  | { tipo: "broll"; desde: number; hasta: number; src: string; trim: number; kb?: [number, number]; ajuste?: "cover"; foco?: number }
  | { tipo: "montaje"; desde: number; hasta: number; clips: { src: string; trim: number }[] }
  | { tipo: "mg-investigar" | "mg-reloj" | "mg-grafica" | "mg-cierre"; desde: number; hasta: number };

const C155 = "broll/Copia de Copia de c155.mp4";
const C87 = "broll/Copia de Copia de c87.mp4";
export const ESCENAS: Escena[] = [
  { tipo: "montaje", desde: 3.0, hasta: 4.17, clips: [ { src: C155, trim: 1.5 }, { src: C155, trim: 2.8 } ] },
  { tipo: "broll", desde: 10.1, hasta: 11.5, src: "proxy/apoyo_3.mp4", trim: 5.0, kb: [1.2, 1.02] },
  { tipo: "broll", desde: 11.5, hasta: 12.2, src: "stock/mk_16007.mp4", trim: 3.0, kb: [1.15, 1.0] },
  { tipo: "mg-investigar", desde: 13.05, hasta: 14.8 },
  {
    tipo: "montaje", desde: 18.15, hasta: 19.8,
    clips: [ { src: C155, trim: 23.3 }, { src: C87, trim: 23.4 }, { src: C87, trim: 21.6 }, { src: C155, trim: 25.0 } ],
  },
  { tipo: "mg-reloj", desde: 21.27, hasta: 23.38 },
  { tipo: "broll", desde: 23.38, hasta: 24.95, src: "stock/mk_43902.mp4", trim: 1.0, kb: [1.3, 1.05] },
  { tipo: "mg-grafica", desde: 24.95, hasta: 29.27 },
  { tipo: "broll", desde: 32.43, hasta: 34.13, src: "proxy/apoyo_2.mp4", trim: 2.9, kb: [1.25, 1.02] },
  { tipo: "mg-cierre", desde: DURACION_VOZ_S, hasta: DURACION_VOZ_S + 1.9 },
];
export const DURACION_TOTAL_S = DURACION_VOZ_S + 1.9;

// ---------- Superposiciones UI sobre el plano hablando ----------
export const UI = {
  almuerzo: { desde: 5.85, hasta: 8.5 }, // tarjeta de cristal "Almuerzo de hoy" con chips
  graficaSube: { desde: 20.0, hasta: 21.27 }, // tarjeta oscura con la curva subiendo
  gomitas: { desde: 30.85, hasta: 32.43 }, // widget "2 gomitas al día"
};

// ---------- Transiciones ----------
export const LIGHT_LEAK = 12.2; // centro del destello (giro del guion: empieza la explicación)
