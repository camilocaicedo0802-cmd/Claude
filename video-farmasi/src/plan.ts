// PLAN DE EDICIÓN v2 · estilo UGC sencillo (ver estilo.md → "Reglas aprendidas").
// Tiempos en segundos de la edición. Los índices de palabras apuntan a src/datos/edicion.json.
import { DURACION_VOZ_S } from "./util";

// ---------- Bloques de subtítulos (palabras pequeñas + 1 destacado) ----------
export type EstiloBloque = "linea" | "detras" | "tecleada" | "broll" | "mg";
export type Bloque = {
  estilo: EstiloBloque;
  desde: number;
  hasta: number;
  pequenas: number[];
  destacado: number[];
  pildora?: number[];
  icono?: string;
  alerta?: boolean;
  impacto?: boolean;
};

const L = (desde: number, hasta: number, pequenas: number[], destacado: number[], icono?: string): Bloque => ({ estilo: "linea", desde, hasta, pequenas, destacado, icono });

export const BLOQUES: Bloque[] = [
  L(0.0, 0.8, [], [0], "saludo"),
  { estilo: "detras", desde: 0.8, hasta: 3.0, pequenas: [1, 2, 3, 4, 5], destacado: [6] }, // gancho
  L(3.0, 4.17, [7], [8]),
  L(4.17, 5.57, [9], [10]),
  L(5.57, 7.45, [11, 12, 13, 14, 15], [16]),
  L(7.45, 8.57, [17, 18], [19]),
  L(8.57, 9.37, [20], [21]),
  L(9.37, 10.1, [22, 23, 24, 25, 26], []),
  L(10.1, 10.9, [], [27]),
  L(10.9, 12.2, [28, 29, 30], [31], "manzana"),
  L(12.2, 13.05, [32, 33, 34], [35]),
  L(13.05, 14.8, [36, 37, 38, 39], [40, 41]),
  L(14.8, 17.0, [42, 43, 44, 45], [46, 47, 48]),
  L(17.0, 18.15, [49, 50], [51]),
  L(18.15, 19.8, [52, 53, 54], [55]),
  { estilo: "detras", desde: 19.8, hasta: 21.27, pequenas: [56], destacado: [57] }, // tema central
  L(21.27, 22.8, [59, 60], [61, 62]),
  L(22.8, 23.38, [63], [64]),
  L(23.38, 24.95, [65, 66, 67, 68, 69, 70, 71], [72, 73, 74]),
  { estilo: "mg", desde: 24.95, hasta: 26.5, pequenas: [75, 76, 77], destacado: [78] }, // MG molécula
  { estilo: "mg", desde: 26.5, hasta: 27.88, pequenas: [79, 80, 81, 82, 83], destacado: [84] }, // MG gráfica
  { estilo: "mg", desde: 27.88, hasta: 29.27, pequenas: [85, 86], destacado: [87] }, // MG gráfica
  L(29.27, 30.5, [88], [89, 90]),
  L(30.5, 31.6, [91, 92, 93], [94, 95]),
  L(31.6, 32.43, [], [96, 97]),
  L(32.43, 34.13, [98, 99, 100], [101, 102]),
  L(34.13, 34.89, [103, 104, 105, 106], [107, 108]),
  L(34.89, 36.9, [109, 110, 111, 112, 113], [114, 115]),
];

// ---------- Escenas: solo b-roll propio del producto, corte seco ----------
export type Escena =
  | { tipo: "broll"; desde: number; hasta: number; src: string; trim: number; kb?: [number, number] }
  | { tipo: "imagen"; desde: number; hasta: number; src: string; kb?: [number, number]; foco?: string }
  | { tipo: "mg-glucosa" | "mg-grafica"; desde: number; hasta: number };
export const ESCENAS: Escena[] = [
  { tipo: "broll", desde: 10.1, hasta: 12.2, src: "proxy/apoyo_3.mp4", trim: 5.0 }, // "gomitas de sidra de manzana"
  // ---- Bloque explicativo de glucosa (b-roll de salud + motion graphics) ----
  { tipo: "imagen", desde: 17.0, hasta: 18.15, src: "img/glucometro_plato.jpg", kb: [1.14, 1.0], foco: "55% 50%" }, // "uno cuando come"
  { tipo: "broll", desde: 18.15, hasta: 19.8, src: "stock/mk_12909.mp4", trim: 1.4, kb: [1.0, 1.06] }, // "cualquier cosa que coma"
  { tipo: "imagen", desde: 21.27, hasta: 22.3, src: "img/medicion_dedo.jpg", kb: [1.12, 1.0], foco: "50% 60%" }, // "y demora mucho tiempo"
  { tipo: "broll", desde: 22.3, hasta: 23.38, src: "stock/mk_31563.mp4", trim: 2.0, kb: [1.1, 1.0] }, // "estando ahí" (en la sangre)
  { tipo: "broll", desde: 23.38, hasta: 24.95, src: "proxy/apoyo_1.mp4", trim: 2.0 }, // "lo que le ayuda la sidra de manzana"
  { tipo: "mg-glucosa", desde: 24.95, hasta: 26.5 }, // "a que esa GLUCOSA"
  { tipo: "mg-grafica", desde: 26.5, hasta: 29.27 }, // "no quede ARRIBA, sino que BAJE"
  // ---- Cierre: ella se echa las gomitas (cola de la toma) y plano del producto ----
  { tipo: "broll", desde: 36.9, hasta: DURACION_VOZ_S + 0.4, src: "proxy/apoyo_3.mp4", trim: 5.4, kb: [1.08, 1.0] },
  { tipo: "broll", desde: 32.43, hasta: 34.13, src: "proxy/apoyo_2.mp4", trim: 2.9 }, // "una antes de la comida"
];
export const DURACION_TOTAL_S = DURACION_VOZ_S + 0.4; // 0,4 s de cola sobre el plano del producto

// ---------- Cámara: apertura suave + alternar 1,00 / 1,07 en cada corte de salto ----------
export type Mov = { t: number; s: number; y: number; d: number; lineal?: boolean };
const CORTES = [0.8, 4.17, 5.57, 8.57, 9.37, 12.2, 14.8, 16.2, 19.8, 21.27, 26.5, 29.27, 30.5, 34.13];
export const CAMARA: Mov[] = [
  { t: 0, s: 1.12, y: 0, d: 0 },
  { t: 0, s: 1.0, y: 0, d: 0.5 },
  ...CORTES.map((t, i) => ({ t, s: i % 2 === 0 ? 1.07 : 1.0, y: 0, d: 0.066 })),
  { t: 1.9, s: 1.07, y: 40, d: 0.3 }, // ESPOSITO detrás (reencuadre leve)
  { t: 4.17, s: 1.0, y: 0, d: 0.066 },
  { t: 19.8, s: 1.07, y: 40, d: 0.066 }, // GLUCOSA detrás
  { t: 21.27, s: 1.0, y: 0, d: 0.066 },
].sort((a, b) => a.t - b.t);

// ---------- Única superposición informativa: tarjeta de glucosa (sube / baja) ----------
export const UI = {
  graficaSube: { desde: 20.0, hasta: 21.27 }, // tarjeta oscura con la curva subiendo (sobre el plano hablando)
  carbohidratos: { desde: 18.15, hasta: 19.8 }, // chip "Carbohidratos → Glucosa" sobre el b-roll del azúcar
  tiempo: { desde: 21.27, hasta: 23.38 }, // tarjeta "2–3 h para normalizarse" sobre medición + glóbulos
  cierre: { desde: 37.05 }, // píldora final sobre el plano del producto
};

// Datos usados en los gráficos (fuentes en el pie de cada gráfico)
export const DATOS = {
  pico: "pico: 1–2 h después de comer",
  normaliza: "2–3 h",
  notaNormaliza: "*En personas sin diabetes. Fuente: Healthline.",
  estudio: "Estudios: el vinagre con las comidas puede reducir el pico de glucosa*",
  notaEstudio: "*Metaanálisis Shishehbor et al., 2017. Gráfico ilustrativo. No sustituye el consejo médico.",
};
